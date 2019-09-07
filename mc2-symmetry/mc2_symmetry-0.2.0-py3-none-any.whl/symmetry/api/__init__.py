import abc
from io import BytesIO
from typing import NamedTuple, List, Iterable, Dict, Set, Optional, Any


class NodeInfo(NamedTuple):
    node_id: str
    host: str
    mac: str = None
    user: str = None
    ssh_port: int = 22

    def get_host_string(self):
        if self.user:
            return "%s@%s:%d" % (self.user, self.host, self.ssh_port)
        else:
            return "%s:%d" % (self.host, self.ssh_port)


class NodeLister(abc.ABC):

    @property
    def nodes(self) -> List[NodeInfo]:
        raise NotImplementedError


class NodeManager(NodeLister):

    @property
    def nodes(self) -> List[NodeInfo]:
        return self.get_nodes()

    def save_node(self, node: NodeInfo) -> bool:
        """
        Creates or updates the given node.

        :param node: the node to save
        :return: true if the node was created, false if it was updated
        """
        raise NotImplementedError

    def remove_node(self, node_id: str) -> bool:
        raise NotImplementedError

    def has_node(self, node_id: str) -> bool:
        raise NotImplementedError

    def get_nodes(self) -> List[NodeInfo]:
        raise NotImplementedError

    def get_node(self, node_id: str) -> NodeInfo:
        for node in self.get_nodes():
            if node.node_id == node_id:
                return node

    def set_node_state(self, node_id: str, state: str):
        raise NotImplementedError

    def get_node_states(self) -> Dict[str, str]:
        raise NotImplementedError

    def synchronize_node_states(self):
        raise NotImplementedError


class NodeCreatedEvent(NamedTuple):
    node_id: str


class NodeUpdatedEvent(NamedTuple):
    node_id: str


class NodeRemovedEvent(NamedTuple):
    node_id: str


class NodeDisconnectedEvent(NamedTuple):
    node_id: str


class NodeActivatedEvent(NamedTuple):
    node_id: str


class BootNodeCommand(NamedTuple):
    node_id: str


class ShutdownNodeCommand(NamedTuple):
    node_id: str


class SuspendNodeCommand(NamedTuple):
    node_id: str


class Telemetry(NamedTuple):
    metric: str
    node: NodeInfo
    time: float
    value: object
    service: str = None


class ClusterInfo(abc.ABC):

    @property
    def nodes(self) -> List[str]:
        raise NotImplementedError

    @property
    def active_nodes(self) -> List[str]:
        raise NotImplementedError

    @property
    def services(self) -> List[str]:
        raise NotImplementedError


class ClusterGateway(abc.ABC):

    @property
    def nodes(self) -> Iterable[NodeInfo]:
        raise NotImplementedError

    def boot(self, nodes: List[str] = None):
        raise NotImplementedError

    def shutdown(self, nodes: List[str] = None):
        raise NotImplementedError

    def suspend(self, nodes: List[str] = None):
        raise NotImplementedError

    def probe_node_states(self, nodes: List[str] = None):
        raise NotImplementedError

    def select_nodes(self, nodes: Iterable[str]):
        if not nodes:
            return self.nodes

        return [node for node in self.nodes if node.node_id in nodes]


class RoutingRecord(NamedTuple):
    service: str
    hosts: List[str]
    weights: List[float]


class RoutingTable(abc.ABC):
    def get_routing(self, service) -> RoutingRecord:
        raise NotImplementedError

    def set_routing(self, record: RoutingRecord):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def list_services(self):
        raise NotImplementedError

    def remove_service(self, service):
        raise NotImplementedError

    def get_routes(self):
        return [self.get_routing(service) for service in self.list_services()]


class Balancer(abc.ABC):

    def next_host(self, service=None):
        raise NotImplementedError


class BalancingPolicy:
    name: str


class UpdatePolicyCommand:
    policy: str
    parameters: Dict[str, Any]

    def __init__(self, policy: str, parameters: Dict[str, Any]) -> None:
        super().__init__()
        self.policy = policy
        self.parameters = parameters


class BalancingPolicyService:

    def get_available_policies(self) -> Dict:
        raise NotImplementedError

    def set_active_policy(self, policy: BalancingPolicy):
        raise NotImplementedError

    def get_active_policy(self) -> Optional[BalancingPolicy]:
        raise NotImplementedError

    def get_policy(self, name: str) -> Optional[BalancingPolicy]:
        return self.get_available_policies().get(name, None)


class ServiceDescription:
    id: str
    name: str
    image: str
    port: str
    command: str = None
    version: str = None
    description: str = None
    maintainer: str = None
    image_file: BytesIO = None
    symmetry_port: str = None  # FIXME

    def __init__(self, id: str, name: str, image: str, port: str, command: str = None, version: str = None,
                 description: str = None, maintainer: str = None, image_file: BytesIO = None,
                 symmetry_port: str = None) -> None:
        super().__init__()
        self.id = id
        self.name = name
        self.image = image
        self.port = port
        self.command = command
        self.version = version
        self.description = description
        self.maintainer = maintainer
        self.image_file = image_file
        self.symmetry_port = symmetry_port


class ServiceStatus(NamedTuple):
    node: str

    '''
    CREATED
    DEPLOYED
    RUNNING
    '''
    status: str


class ServiceInfo(NamedTuple):
    description: ServiceDescription
    status: List[ServiceStatus]


class ServiceMetadataRepository(abc.ABC):

    def save_service(self, service: ServiceDescription) -> bool:
        """
        Creates or updates the given service.

        :param service: the node to save
        :return: true if the service was created, false if it was updated
        """
        raise NotImplementedError

    def remove_service(self, service_id: str) -> bool:
        raise NotImplementedError

    def has_service(self, service_id: str) -> bool:
        raise NotImplementedError

    def get_services(self) -> List[ServiceDescription]:
        raise NotImplementedError

    def get_service(self, service_id: str) -> ServiceDescription:
        for service in self.get_services():
            if service.id == service_id:
                return service

    def set_service_hosts(self, service_id: str, *args: NodeInfo):
        raise NotImplementedError

    def get_service_hosts(self, service_id: str) -> Set[str]:
        raise NotImplementedError


class ServiceManager(abc.ABC):

    def create(self, service: ServiceDescription):
        raise NotImplementedError

    def describe(self, service_id: str) -> ServiceDescription:
        raise NotImplementedError

    def remove(self, service_id: str):
        raise NotImplementedError

    def deploy(self, service_id: str):
        raise NotImplementedError

    def undeploy(self, service_id: str):
        raise NotImplementedError

    def destroy(self, service_id: str):
        raise NotImplementedError

    def info(self, service_id: str) -> ServiceInfo:
        raise NotImplementedError
