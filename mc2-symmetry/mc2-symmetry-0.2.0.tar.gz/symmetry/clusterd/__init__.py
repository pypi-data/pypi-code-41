import inspect
import logging
import queue
import socket
import threading
from collections import defaultdict
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List, Optional

import pymq
import wakeonlan
from pymq.exceptions import RemoteInvocationError
from pymq.typing import deep_to_dict

import symmetry.clusterd.policies
from symmetry.api import ClusterInfo, RoutingTable, ServiceMetadataRepository, UpdatePolicyCommand, BalancingPolicy, \
    BalancingPolicyService, BootNodeCommand, NodeManager, NodeInfo, ShutdownNodeCommand, SuspendNodeCommand
from symmetry.clusterd.policies.balancing import BalancingPolicyProvider
from symmetry.common.cluster import RedisNodeManager, is_up, create_connection
from symmetry.common.ssh import ExecutionException
from symmetry.common.typing import isderived, deep_from_dict
from symmetry.nrg import RedisServiceMetadataRepository
from symmetry.routing import RedisRoutingTable
from symmetry.telemetry.recorder import TelemetrySubscriber

logger = logging.getLogger(__name__)


class RedisClusterInfo(ClusterInfo):
    node_manager: RedisNodeManager
    rtbl: RoutingTable
    service_repository: ServiceMetadataRepository
    telemc: TelemetrySubscriber

    def __init__(self, rds) -> None:
        super().__init__()
        self.rds = rds
        self.node_manager = RedisNodeManager(rds)
        self.rtbl = RedisRoutingTable(rds)
        self.telemc = TelemetrySubscriber(rds)
        self.service_repository = RedisServiceMetadataRepository(rds)

    @property
    def nodes(self) -> List[str]:
        return self.node_manager.get_node_ids()

    @property
    def active_nodes(self) -> List[str]:
        states = self.node_manager.get_node_states()
        return [node for node, state in states.items() if state == 'online']

    @property
    def services(self) -> List[str]:
        services = self.service_repository.get_services()
        return [service.id for service in services]


class DefaultBalancingPolicyService(BalancingPolicyService):
    modules = [policies.balancing]

    def __init__(self, bus=None, modules=None) -> None:
        super().__init__()
        self.bus = bus or pymq

        if modules:
            self.modules = modules

    def get_available_policies(self):
        def is_policy(member):
            return isderived(member, BalancingPolicy)

        return {name: obj for module in self.modules for name, obj in inspect.getmembers(module, predicate=is_policy)}

    def set_active_policy(self, policy: BalancingPolicy):
        self.bus.publish(UpdatePolicyCommand(policy.name, deep_to_dict(policy)))

    def get_active_policy(self) -> Optional[BalancingPolicy]:
        try:
            remote = self.bus.stub(BalancingPolicyDaemon.get_active_policy, timeout=2)
            return remote()
        except RemoteInvocationError:
            logger.exception('Could not get active policy from balancing policy daemon')
            return None


class BalancingPolicyDaemon:
    _POISON = '__POISON__'

    _rtbl: RoutingTable
    _cluster: ClusterInfo

    _queue: queue.Queue
    _runner: ThreadPoolExecutor = None
    _stopped: bool

    _policy: Optional[BalancingPolicy]
    _provider: Optional[BalancingPolicyProvider]

    def __init__(self, cluster: ClusterInfo, rtbl: RoutingTable) -> None:
        super().__init__()
        self._cluster = cluster
        self._rtbl = rtbl

        self._queue = queue.Queue()
        self._stopped = False
        self._provider = None
        self._policy = None

        self._provider_factory = policies.balancing_policy_provider_factory()

        pymq.subscribe(self._on_update_policy_command)
        pymq.expose(self.get_active_policy)

    def _on_update_policy_command(self, event: UpdatePolicyCommand):
        # TODO: error handling
        policy_type = policies.balancing_policies()[event.policy]
        policy = deep_from_dict(event.parameters, policy_type)
        self.set_policy(policy)

    def run(self):
        self._runner = ThreadPoolExecutor(max_workers=1)
        try:
            while not self._stopped:
                elem = self._queue.get()

                if elem == self._POISON:
                    break

                policy, provider = elem
                self._stop_current_provider()
                self._start_provider(provider)
                self._policy = policy
        finally:
            self._stop_current_provider()

        logger.debug('balancing daemon has stopped')

    def set_policy(self, policy: BalancingPolicy):
        if self._stopped:
            return

        logger.debug('setting new balancing policy %s', policy)
        provider = self._provider_factory(policy, self._cluster, self._rtbl)
        self._queue.put((policy, provider))

    def get_active_policy(self) -> Optional[BalancingPolicy]:
        return self._policy

    def close(self):
        logger.info('closing BalancingPolicyDaemon')
        self._stopped = True
        self._queue.put(self._POISON)
        if self._runner:
            self._runner.shutdown()

    def _stop_current_provider(self):
        if self._provider:
            try:
                logger.debug('stopping current balancing policy provider %s', self._provider)
                self._provider.close()
            finally:
                self._provider = None

    def _start_provider(self, provider: BalancingPolicyProvider):
        if not self._runner:
            raise ValueError('no active runner')

        if self._provider:
            raise ValueError('current provider needs to be stopped first')

        logger.debug('starting balancing policy provider %s', provider)
        self._provider = provider
        self._runner.submit(provider.run)


class NodeManagerDaemon:
    node_manager: NodeManager

    def __init__(self, node_manager: NodeManager) -> None:
        super().__init__()
        self.node_manager = node_manager

        self.executor = ThreadPoolExecutor()
        self.locks = defaultdict(threading.Lock)
        pymq.subscribe(self._on_boot_node_command)
        pymq.subscribe(self._on_shutdown_node_command)
        pymq.subscribe(self._on_suspend_node_command)

    def close(self):
        logger.debug('closing NodeManagerDaemon')

        pymq.unsubscribe(self._on_boot_node_command)
        pymq.unsubscribe(self._on_shutdown_node_command)
        pymq.unsubscribe(self._on_suspend_node_command)

        self.executor.shutdown()

    def _on_boot_node_command(self, cmd: BootNodeCommand):
        logger.debug('received boot command for node %s', cmd.node_id)

        node = self.node_manager.get_node(cmd.node_id)
        if not node:
            return
        self.executor.submit(self._do_boot, node)

    def _on_shutdown_node_command(self, cmd: ShutdownNodeCommand):
        logger.debug('received shutdown command for node %s', cmd.node_id)

        node = self.node_manager.get_node(cmd.node_id)
        if not node:
            return
        self.executor.submit(self._do_shutdown, node)

    def _on_suspend_node_command(self, cmd: SuspendNodeCommand):
        logger.debug('received suspend command for node %s', cmd.node_id)

        node = self.node_manager.get_node(cmd.node_id)
        if not node:
            return
        self.executor.submit(self._do_suspend, node)

    def _do_boot(self, node: NodeInfo):
        wakeonlan.send_magic_packet(node.mac)

    def _do_shutdown(self, node: NodeInfo):
        with self.locks[node.node_id]:
            if not is_up(node):
                logger.debug('received shutdown command, but node was offline %s', node.node_id)
                return

            con = create_connection(node)
            con.kwargs['timeout'] = 5
            con.kwargs['banner_timeout'] = 5
            con.kwargs['auth_timeout'] = 5

            logger.info('attempting to shut down node %s', node.node_id)
            con.ensure_connection()
            try:
                con.run('shutdown -h now', timeout=5)
            except:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.exception('could not shut down node %s', node)
            finally:
                con.close()

    def _do_suspend(self, node: NodeInfo):
        with self.locks[node.node_id]:
            if not is_up(node):
                logger.debug('received suspend command, but node was offline %s', node.node_id)
                return

            con = create_connection(node)
            con.kwargs['timeout'] = 5
            con.kwargs['banner_timeout'] = 5
            con.kwargs['auth_timeout'] = 5

            logger.info('attempting to suspend node %s', node.node_id)
            con.ensure_connection()
            try:
                # https://askubuntu.com/questions/1792/how-can-i-suspend-hibernate-from-command-line
                con.run('systemctl suspend', timeout=5)
            except ExecutionException as e:
                if isinstance(e.result.error, socket.timeout):
                    logger.debug('command timed out as expected')
                else:
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.exception('could not shut down node %s', node)
            finally:
                con.close()
