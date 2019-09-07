"""
Node Manager.
"""
import configparser
import logging
import socket
from concurrent.futures import ThreadPoolExecutor

import pymq
import redis
from wakeonlan import send_magic_packet

from symmetry.api import *
from symmetry.common.ssh import Connection, ConnectionGroup, ThreadedConnectionGroup, GroupResult, \
    GroupExecutionException

logger = logging.getLogger(__name__)


def create_connection(node: NodeInfo) -> Connection:
    """
    Creates an ssh Connection object using the parameters from the given NodeInfo.

    :param node: the node info
    :return: a Connection object
    """
    logger.debug('creating connection for %s', node)

    return Connection(
        hostname=node.host,
        port=int(node.ssh_port),
        username=node.user,
    )


def is_up(node: NodeInfo) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(0.5)
        s.connect((node.host, int(node.ssh_port)))
        return True
    except OSError:
        return False
    except Exception as e:
        raise e
    finally:
        s.close()


def probe_nodes(nodes: List[NodeInfo]) -> Dict[str, bool]:
    result = dict()

    if not nodes:
        logger.debug('no nodes to probe')
        return result

    with ThreadPoolExecutor(max_workers=len(nodes)) as ex:
        for n in nodes:
            logger.debug("submitting status check for node %s", n)
            result[n.node_id] = ex.submit(is_up, n)

    # materialize
    for k, future in result.items():
        result[k] = future.result()
        logger.debug("result of status check for node %s: %s", k, result[k])

    return result


class ConfigNodeLister(NodeLister):

    def __init__(self, fpath='nodes.ini') -> None:
        self._nodes = self.parse_config(fpath)

    @property
    def nodes(self) -> List[NodeInfo]:
        return self._nodes

    @staticmethod
    def parse_config(ini_file) -> List[NodeInfo]:
        config = configparser.ConfigParser()
        logger.debug('reading ini file %s', ini_file)
        config.read(ini_file)
        nodes = list()
        for sec in config.sections():
            params = config[sec]

            node = NodeInfo(node_id=sec, host=params.get('host'), mac=params.get('mac'), user=params.get('user'),
                            ssh_port=int(params.get('port', 22)))
            logger.debug('node info parsed: %s', node)
            nodes.append(node)
        logger.debug('found %d nodes in config', len(nodes))
        return nodes


class NodeStateUpdateListener:

    def __init__(self, node_manager: NodeManager) -> None:
        super().__init__()
        self.node_manager = node_manager

        pymq.subscribe(self._on_node_activated)
        pymq.subscribe(self._on_node_disconnected)

    def _on_node_activated(self, event: NodeActivatedEvent):
        self.node_manager.set_node_state(event.node_id, 'online')

    def _on_node_disconnected(self, event: NodeDisconnectedEvent):
        self.node_manager.set_node_state(event.node_id, 'offline')


class NodeOperationNotifierDecorator(NodeManager):

    def __init__(self, delegate: NodeManager) -> None:
        super().__init__()
        self.delegate = delegate

    def save_node(self, node: NodeInfo) -> bool:
        new = self.delegate.save_node(node)

        if new:
            pymq.publish(NodeCreatedEvent(node.node_id))
        else:
            pymq.publish(NodeUpdatedEvent(node.node_id))

        return new

    def remove_node(self, node_id: str):
        deleted = self.delegate.remove_node(node_id)
        if deleted:
            pymq.publish(NodeRemovedEvent(node_id))
        return deleted

    def has_node(self, node_id: str) -> bool:
        return self.delegate.has_node(node_id)

    def get_nodes(self) -> List[NodeInfo]:
        return self.delegate.get_nodes()

    def set_node_state(self, node_id: str, state: str):
        return self.delegate.set_node_state(node_id, state)

    def get_node_states(self) -> Dict[str, str]:
        return self.delegate.get_node_states()

    def synchronize_node_states(self):
        return self.delegate.synchronize_node_states()


class RedisNodeManager(NodeManager):
    rds: redis.Redis

    '''
    symmetry:nodes = set
    symmetry:nodes:{node} = hash (NodeInfo)
    symmetry:nodes:{node}:state = string
    '''

    def __init__(self, rds: redis.Redis) -> None:
        super().__init__()
        self.rds = rds

    def save_node(self, node: NodeInfo) -> bool:
        pipe = self.rds.pipeline()
        self._pipeline_save_node(node, pipe)
        result = pipe.execute()

        return result[0] == 1  # first element is the result of 'sadd' which will be 1 if the item was added

    def remove_node(self, node_id: str) -> bool:
        pipe = self.rds.pipeline()
        pipe.srem('symmetry:nodes', node_id)
        pipe.delete(f'symmetry:nodes:{node_id}', f'symmetry:nodes:{node_id}:state')
        result = pipe.execute()

        return result[0] == 1

    def has_node(self, node_id: str) -> bool:
        return self.rds.sismember('symmetry:nodes', node_id)

    def get_node_ids(self) -> List[str]:
        return list(self.rds.smembers('symmetry:nodes'))

    def get_nodes(self) -> List[NodeInfo]:
        node_ids = self.get_node_ids()

        pipe = self.rds.pipeline()

        for node_id in node_ids:
            k = f'symmetry:nodes:{node_id}'
            pipe.hgetall(k)

        result = pipe.execute()
        items = [item for item in result if item]
        return [NodeInfo(**item) for item in items]

    def set_node_state(self, node_id: str, state: str):
        key = f'symmetry:nodes:{node_id}:state'
        self.rds.set(key, state)

    def get_node_states(self) -> Dict[str, str]:
        node_ids = self.get_node_ids()

        pipe = self.rds.pipeline()

        for node_id in node_ids:
            k = f'symmetry:nodes:{node_id}:state'
            pipe.get(k)

        result = pipe.execute()

        return {node_ids[i]: result[i] for i in range(len(node_ids))}

    def synchronize_node_states(self):
        nodes = self.get_nodes()
        if not nodes:
            return

        states = probe_nodes(nodes)
        states = {node: 'online' if up else 'offline' for node, up in states.items()}
        self.set_node_states(states)

    def set_node_states(self, states: Dict[str, str]):
        pipe = self.rds.pipeline()

        for node_id, state in states.items():
            pipe.set(f'symmetry:nodes:{node_id}:state', state)

        pipe.execute()

    @staticmethod
    def _pipeline_save_node(node, pipe):
        pipe.sadd('symmetry:nodes', node.node_id)
        hkey = f'symmetry:nodes:{node.node_id}'
        for k, v in node._asdict().items():
            if v is None:
                continue
            pipe.hset(hkey, k, v)


class DefaultClusterGateway(ClusterGateway):

    def __init__(self, node_manager: NodeManager) -> None:
        super().__init__()
        self.node_manager = node_manager

    @property
    def nodes(self) -> List[NodeInfo]:
        return self.node_manager.get_nodes()

    def suspend(self, nodes: List[str] = None):
        if not nodes:
            nodes = [node.node_id for node in self.nodes]

        for node_id in nodes:
            logger.debug('issuing suspend node command for %s', node_id)
            pymq.publish(SuspendNodeCommand(node_id))

    def shutdown(self, nodes: List[str] = None):
        if not nodes:
            nodes = [node.node_id for node in self.nodes]

        for node_id in nodes:
            logger.debug('issuing shutdown node command for %s', node_id)
            pymq.publish(ShutdownNodeCommand(node_id))

    def boot(self, nodes: List[str] = None):
        if not nodes:
            nodes = [node.node_id for node in self.nodes]

        for node_id in nodes:
            logger.debug('issuing boot node command for %s', node_id)
            pymq.publish(BootNodeCommand(node_id))

    def probe_node_states(self, nodes: List[str] = None):
        return probe_nodes(self.select_nodes(nodes))

    @staticmethod
    def is_up(node: NodeInfo):
        return is_up(node)
