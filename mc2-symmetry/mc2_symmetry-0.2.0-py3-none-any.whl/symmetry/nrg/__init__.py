import abc
import logging
import time
from concurrent import futures
from typing import List, Set, Dict

import docker
import jinja2
import redis
from redis.client import Pipeline

from symmetry.api import NodeInfo
from symmetry.api import ServiceMetadataRepository, ServiceDescription, NodeLister, ServiceManager, \
    ServiceInfo, ServiceStatus
from symmetry.common.ssh import Connection

logger = logging.getLogger(__name__)


class RedisServiceMetadataRepository(ServiceMetadataRepository):
    rds: redis.Redis

    '''
    symmetry:services = set
    symmetry:service:{service} = hash (ServiceDescription)
    symmetry:service:{service}:hosts = set
    '''

    def __init__(self, rds: redis.Redis) -> None:
        super().__init__()
        self.rds = rds

    def save_service(self, service: ServiceDescription) -> bool:
        pipe = self.rds.pipeline()
        self._pipeline_save_service(service, pipe)
        result = pipe.execute()

        return result[0] == 1

    def remove_service(self, service_id: str) -> bool:
        pipe = self.rds.pipeline()
        pipe.srem('symmetry:services', service_id)
        pipe.delete(f'symmetry:service:{service_id}', f'symmetry:service:{service_id}:hosts')
        result = pipe.execute()

        return result[0] == 1

    def has_service(self, service_id: str) -> bool:
        return self.rds.sismember('symmetry:services', service_id)

    def get_services(self) -> List[ServiceDescription]:
        pipe = self.rds.pipeline()

        for service_id in list(self.rds.smembers('symmetry:services')):
            hkey = f'symmetry:service:{service_id}'
            pipe.hgetall(hkey)

        result = pipe.execute()
        return [ServiceDescription(**item) for item in result if item]

    def set_service_hosts(self, service_id: str, *args: NodeInfo):
        pipe = self.rds.pipeline()

        for node in args:
            pipe.sadd(f'symmetry:services:{service_id}:hosts', node.host)

        pipe.execute()

    def get_service_hosts(self, service_id: str) -> Set[str]:
        pipe = self.rds.pipeline()

        pipe.smembers(f'symmetry:service:{service_id}:hosts')

        result = pipe.execute()
        return result[0]

    @staticmethod
    def _pipeline_save_service(service: ServiceDescription, pipe: Pipeline):
        pipe.sadd('symmetry:services', service.id)
        hkey = f'symmetry:service:{service.id}'
        for k, v in service.__dict__.items():
            if v is None:
                pipe.hdel(hkey, k)
                continue
            pipe.hset(hkey, k, v)


class NginxProxyConfigurator:
    _template_string = '''
        location /{{ service_id }} {
            rewrite ^/{{ service_id }}/(.*)$ /$1 break;
            rewrite ^/{{ service_id }}(.*)$ /$1 break;
            proxy_pass         http://{{ host }}:{{ service_port }};
            proxy_redirect     off;
            proxy_set_header   Host $host;
            proxy_set_header   X-Real-IP $remote_addr;
            proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Host $server_name;
        }
    '''
    _template: jinja2.Template

    def __init__(self) -> None:
        super().__init__()
        self._template = jinja2.Environment(loader=jinja2.BaseLoader()).from_string(self._template_string)

    def list_existing_entries(self, node_ip):
        with Connection(node_ip, username='root') as ssh:
            result = ssh.run('find /etc/nginx/symmetry -name "*.conf" -printf "%f\n"')
            return [entry.rstrip('.conf') for entry in result.result.split('\n')]

    def create_entry(self, node_ip, service_id, service_port):
        with Connection(node_ip, username='root') as ssh:
            ssh.open_sftp()
            ssh.change_sftp_dir(path='/etc/nginx/symmetry')

            new_config = self._render_config(service_id, service_port)

            with ssh.get_sftp_file('%s.conf' % service_id, mode='w') as config:
                config.write(new_config)

            ssh.run('nginx -s reload')

    def remove_entry(self, node_ip, service_id):
        if not service_id:
            raise ValueError
        if service_id == '*':
            raise ValueError

        with Connection(node_ip, username='root') as ssh:
            try:
                ssh.run('rm -f /etc/nginx/symmetry/%s.conf && nginx -s reload' % service_id)
            finally:
                ssh.close()

    def _render_config(self, service_id, service_port, host='localhost'):
        return self._template.render(host=host, service_id=service_id, service_port=service_port)


class DockerGateway:

    def __init__(self) -> None:
        super().__init__()
        self.docker_port = '2376'

    def start_service_container(self, node_ip, service: ServiceDescription, port):
        client = docker.DockerClient(base_url='tcp://' + node_ip + ':' + self.docker_port)

        if service.image_file:
            images = client.images.load(service.image_file)
            if service.image not in images[0].tags:
                raise ValueError(f'given tag ({service.image}) must be provided by uploaded image')

        ports = {
            service.port: port
        }

        client.containers.run(service.image, command=service.command, detach=True, name=service.id, ports=ports)
        client.close()

    def list_containers(self, node_ip):
        client = docker.DockerClient(base_url='tcp://' + node_ip + ':' + self.docker_port)
        try:
            return client.containers.list(all=True)
        finally:
            client.close()

    def remove_service_container(self, node_ip, service_id):
        client = docker.DockerClient(base_url='tcp://' + node_ip + ':' + self.docker_port)
        container = client.containers.get(service_id)
        container.remove(force=True)
        client.close()


class PortAllocator(abc.ABC):
    port_range: range = range(11000, 12000)

    def allocate_port(self) -> int:
        raise NotImplementedError


class UnsafePortAllocator(PortAllocator):
    """
    Allocates ports based on which ones are registered in the metadata repository. It is unsafe because it may hand out
    the same port twice if the port has not been registered in the metadata repository before calling allocate_port
    again.
    """

    def __init__(self, metadata: ServiceMetadataRepository) -> None:
        super().__init__()
        self._metadata = metadata

    def allocate_port(self) -> int:
        ports = set(self.port_range)
        used = {int(service.symmetry_port) for service in self._metadata.get_services() if service.symmetry_port}
        ports.difference_update(used)

        if len(ports) == 0:
            raise ValueError('No available ports for service allocation')

        return ports.pop()


class LeasingPortAllocator(PortAllocator):
    """
    This allocator uses the service metadata repository and port leases to determine used ports, which fixes the issue
    of UnsafePortAllocator (at least for one thread). Every time a port is allocated, the allocator creates a lease for
    the port, which expires after 2 minutes. It still does not solve the problem that the port may not actually be
    available on the cluster node for which the port is being allocated.
    """
    timeout: int = 120  # 2 minutes

    def __init__(self, metadata: ServiceMetadataRepository) -> None:
        super().__init__()
        self._metadata = metadata
        self._leases: Dict[int, float] = dict()

    def _expire_leases(self):
        th = time.time() - self.timeout

        expired = {port for port, t in self._leases.items() if th > t}
        for port in expired:
            del self._leases[port]

    def allocate_port(self) -> int:
        self._expire_leases()

        ports = set(self.port_range)

        used = {int(service.symmetry_port) for service in self._metadata.get_services() if service.symmetry_port}
        leased = set(self._leases.keys())
        ports.difference_update(used, leased)

        if len(ports) == 0:
            raise ValueError('No available ports for service allocation')

        port = ports.pop()
        self._leases[port] = time.time()
        return port


class DefaultServiceManager(ServiceManager):
    _worker_threads: int = 4

    _nginx_config: NginxProxyConfigurator
    _docker: DockerGateway
    _metadata: ServiceMetadataRepository

    def __init__(self, metadata: ServiceMetadataRepository, node_lister: NodeLister) -> None:
        super().__init__()
        self._metadata = metadata
        self._node_lister = node_lister

        self._port_allocator = UnsafePortAllocator(metadata)
        self._nginx_config = NginxProxyConfigurator()
        self._docker = DockerGateway()

    def create(self, service: ServiceDescription):
        if self._metadata.has_service(service.id):
            raise ValueError('service exists')

        self._metadata.save_service(service)

    def describe(self, service_id: str) -> ServiceDescription:
        return self._metadata.get_service(service_id)

    def remove(self, service_id: str):
        # TODO check if has deployment, if not, raise value error (to undeploy first)
        self._metadata.remove_service(service_id)

    def deploy(self, service_id: str):
        description = self._metadata.get_service(service_id)
        if description is None:
            raise ValueError('no such service %s' % service_id)

        self._deploy_service(description)

    def undeploy(self, service_id: str):
        service = self.describe(service_id)
        if not service:
            raise ValueError('no such service %s' % service_id)
        self._undeploy_service(service)

    def destroy(self, service_id: str):
        service = self.describe(service_id)
        if not service:
            raise ValueError('no such service %s' % service_id)

        self._undeploy_service(service)
        self._metadata.remove_service(service.id)

    def _probe_container_status(self, service_id: str, node_ip):
        containers = self._docker.list_containers(node_ip)
        for container in containers:
            if container.name == service_id:
                return container.status

    def info(self, service_id: str) -> ServiceInfo:
        description = self.describe(service_id)
        if not description:
            raise ValueError('no such service %s' % service_id)

        status_list = list()

        nodes = list(self._node_lister.nodes)

        with futures.ThreadPoolExecutor(max_workers=self._worker_threads) as executor:
            threads = [executor.submit(self._probe_container_status, service_id, node.host) for node in nodes]

            futures.wait(threads, return_when=futures.FIRST_EXCEPTION)
            containers = [thread.result() for thread in threads]

        for i in range(len(nodes)):
            node = nodes[i]
            container = containers[i]
            status = container if container else 'created'
            status_list.append(ServiceStatus(node.node_id, status))

        return ServiceInfo(description, status_list)

    def _deploy_node_service(self, node_ip: str, service: ServiceDescription, port: int):
        self._docker.start_service_container(node_ip, service, port)
        self._nginx_config.create_entry(node_ip, service.id, port)

    def _undeploy_node_service(self, node_ip, service_id: str):
        self._docker.remove_service_container(node_ip, service_id)
        self._nginx_config.remove_entry(node_ip, service_id)

    def _deploy_service(self, service: ServiceDescription):
        if service.symmetry_port is None:
            service.symmetry_port = self._port_allocator.allocate_port()

        self._metadata.save_service(service)

        nodes = self._node_lister.nodes

        with futures.ThreadPoolExecutor(max_workers=self._worker_threads) as executor:
            threads = [executor.submit(self._deploy_node_service, n.host, service, service.symmetry_port) for n in
                       nodes]
            futures.wait(threads, return_when=futures.FIRST_EXCEPTION)
            for thread in threads:
                thread.result()

        self._metadata.set_service_hosts(service.id, *nodes)

    def _undeploy_service(self, service: ServiceDescription):
        nodes = self._node_lister.nodes
        with futures.ThreadPoolExecutor(max_workers=self._worker_threads) as executor:
            threads = [executor.submit(self._undeploy_node_service, n.host, service.id) for n in nodes]
            futures.wait(threads, return_when=futures.FIRST_EXCEPTION)
            for thread in threads:
                thread.result()
        return service
