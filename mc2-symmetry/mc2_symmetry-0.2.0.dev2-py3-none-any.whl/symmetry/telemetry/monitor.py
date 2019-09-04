import abc
import logging
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Callable, Union, Iterable

from paramiko.ssh_exception import SSHException

from symmetry.api import NodeInfo, Telemetry
from symmetry.common.cluster import create_connection, is_up
from symmetry.common.niossh import ChannelEventLoop, CommandCallback, Result, ResultCollector, ResultHandler
from symmetry.common.scheduler import Scheduler, ScheduledTask
from symmetry.common.ssh import Connection

logger = logging.getLogger(__name__)


class TelemetryCommand:

    def __init__(self, command: str, parser: 'TelemetryDataParser') -> None:
        super().__init__()
        self.command: str = command
        self.parser: 'TelemetryDataParser' = parser


TelemetryDataListener = Callable[[TelemetryCommand, Telemetry], None]
TelemetryErrorListener = Callable[[TelemetryCommand, NodeInfo, Exception], None]
TelemetryDataParser = Callable[[TelemetryCommand, NodeInfo, Result], Union[Telemetry, Iterable[Telemetry]]]


class NodeStateListener(abc.ABC):
    def on_disconnect(self, node_info: NodeInfo):
        pass

    def on_activate(self, node_info: NodeInfo):
        pass


class MonitorEventDispatcher:

    def __init__(self) -> None:
        super().__init__()
        self.executor: ThreadPoolExecutor = ThreadPoolExecutor(4, thread_name_prefix='monitor_dispatch')

        self.data_listeners: List[TelemetryDataListener] = list()
        self.error_listeners: List[TelemetryErrorListener] = list()
        self.node_state_listeners: List[NodeStateListener] = list()

    def fire_on_activate(self, node_info):
        for fn in self.node_state_listeners:
            self.executor.submit(fn.on_activate, node_info)

    def fire_on_disconnect(self, node_info):
        for fn in self.node_state_listeners:
            self.executor.submit(fn.on_disconnect, node_info)

    def fire_on_data(self, command: TelemetryCommand, data: Telemetry):
        for fn in self.data_listeners:
            self.executor.submit(fn, command, data)

    def fire_on_exception(self, command: TelemetryCommand, data: Telemetry, exception):
        for fn in self.error_listeners:
            self.executor.submit(fn, command, data, exception)

    def shutdown(self):
        self.executor.shutdown()


class _TelemetryCommandCallback(CommandCallback):
    """
    Adapter class for firing listeners of an EventBasedClusterMonitor as a CommandCallback.
    """

    def __init__(self, command, dispatcher: MonitorEventDispatcher) -> None:
        super().__init__()
        self.command: TelemetryCommand = command
        self.dispatcher = dispatcher

    def on_result(self, result: Result):
        node_info = result.node_info  # given by NodeResultCollector

        if (not result.stdout and not result.stderr) or (len(result.stdout) == 0):
            return

        try:
            data = self.command.parser(self.command, node_info, result)
        except Exception as e:
            # TODO: command parsing went wrong
            logger.error('error during command parsing %s %s', self.command.command, e)
            return

        if not data:
            return

        if isinstance(data, Telemetry):
            self.dispatcher.fire_on_data(self.command, data)
        else:
            for d in data:
                self.dispatcher.fire_on_data(self.command, d)

    def on_exception(self, node_info, exception):
        self.dispatcher.fire_on_exception(self.command, node_info, exception)


class _NodeResultCollector(ResultCollector):
    """
    Appends a node_info object to the Result before the handler is called.
    """

    def __init__(self, node_info, handler: ResultHandler, aggregate=True, closed_handler=None) -> None:
        super().__init__(handler, aggregate)
        self.node_info = node_info
        self.closed_handler = closed_handler

    def on_result(self, channel, result: Result):
        result.node_info = self.node_info
        super().on_result(channel, result)

    def on_transport_closed(self, channel):
        if self.closed_handler:
            self.closed_handler(self.node_info)


class EventBasedClusterMonitor:
    retry_interval: int = 5

    # global state lock
    _lock: threading.Lock

    _nodes: Dict[str, NodeInfo]
    _active_nodes: Dict[str, NodeInfo]
    _connections: Dict[str, Connection]
    _scheduled_task: Dict[str, List[ScheduledTask]]

    _event_loop: ChannelEventLoop
    _event_dispatcher: MonitorEventDispatcher
    _scheduler: Scheduler

    def __init__(self) -> None:
        super().__init__()
        self._lock = threading.Lock()  # state lock
        self._nodes = dict()
        self._active_nodes = dict()
        self._connections = dict()
        self._scheduled_tasks = dict()

        self._event_loop = ChannelEventLoop()
        self._event_dispatcher = MonitorEventDispatcher()
        self._scheduler = Scheduler(ThreadPoolExecutor(4, thread_name_prefix='monitor_task'))

        self._t_read_loop = None
        self._t_scheduler = None

    def add_data_listener(self, listener: TelemetryDataListener):
        self._event_dispatcher.data_listeners.append(listener)

    def add_error_listener(self, listener: TelemetryErrorListener):
        self._event_dispatcher.error_listeners.append(listener)

    def add_node_state_listener(self, listener: NodeStateListener):
        self._event_dispatcher.node_state_listeners.append(listener)

    def start(self):
        with self._lock:
            self._t_read_loop = threading.Thread(target=self._event_loop.run, name='monitor-read-loop')
            self._t_read_loop.start()

            self._t_scheduler = threading.Thread(target=self._scheduler.run, name='monitor-scheduler')
            self._t_scheduler.start()

    def add_node(self, node: NodeInfo):
        with self._lock:
            if node.node_id in self._nodes:
                return False

            self._nodes[node.node_id] = node
            self._scheduled_tasks[node.node_id] = list()

            logger.info('creating connection object for node %s', node.node_id)
            self._connections[node.node_id] = create_connection(node)

            logger.info('scheduling activation for node %s', node.node_id)
            self._scheduler.schedule(self._do_try_activate, args=(node.node_id,))
            return True

    def schedule(self, command: TelemetryCommand, period: float):
        callback = _TelemetryCommandCallback(command, self._event_dispatcher)

        with self._lock:
            for node in self._nodes.values():
                task = ScheduledTask(self._do_exec_command, period=period, args=(node, command.command, callback))

                logger.debug('scheduling periodic command %s for node %s', command.__class__.__name__, node.node_id)
                self._scheduled_tasks[node.node_id].append(task)

                if node.node_id in self._active_nodes:
                    self._scheduler.schedule_task(task)

    def listen(self, command: TelemetryCommand):
        # FIXME: listen-command tracking does not work, they will not be rescheduled! commands that listen need to be
        #  tracked differently. one way could be to use the 'on_eof' method of the ChannelHandlers. perhaps that is too
        #  low in the abstraction, however.
        callback = _TelemetryCommandCallback(command, self._event_dispatcher)

        with self._lock:
            for node in self._nodes.values():
                task = ScheduledTask(self._do_exec_command, args=(node, command.command, callback, True))

                logger.debug('scheduling listen command %s for node %s', command.__class__.__name__, node.node_id)
                self._scheduled_tasks[node.node_id].append(task)

                if node.node_id in self._active_nodes:
                    self._scheduler.schedule_task(task)

    def remove_node(self, node_id: str):
        with self._lock:
            node = self._nodes.get(node_id)
            if node is None:
                return False

            connection = self._connections[node_id]
            tasks = self._scheduled_tasks[node_id]

            for task in tasks:
                task.cancel()

            tasks.clear()

            del self._nodes[node.node_id]
            del self._connections[node_id]
            del self._active_nodes[node_id]
            del self._scheduled_tasks[node_id]

        if connection.is_connected:
            self._event_dispatcher.fire_on_disconnect(node)

        try:
            connection.disconnect()
        except:
            pass

    def stop(self):
        logger.debug('closing scheduler')
        self._close()

        self._scheduler.close()
        if self._scheduler.executor:
            logger.debug('shutting down scheduler executor')
            self._scheduler.executor.shutdown()

        logger.debug('closing event loop')
        self._event_loop.close()

        logger.debug('shutting down event dispatcher')
        self._event_dispatcher.shutdown()

        logger.debug('waiting for scheduler thread')
        self._t_scheduler.join()
        logger.debug('waiting for read loop')
        self._t_read_loop.join()

    def _close(self):
        with self._lock:
            # cancel all schedule tasks
            for node_id, tasks in self._scheduled_tasks.items():
                for task in tasks:
                    task.cancel()
                tasks.clear()
            self._scheduled_tasks.clear()

            # copy list of connections to close outside lock
            connections = list(self._connections.values())

            # clear state
            self._connections.clear()
            self._nodes.clear()
            self._active_nodes.clear()

        logger.debug('attempting to close %d connections', len(connections))
        for connection in connections:
            try:
                logger.debug('attempting to close %s', connection)
                connection.close()
            except:
                pass

    def _on_node_disconnect(self, node: NodeInfo):
        """
        Detecting disconnected nodes is done opportunistically: every command may call this function, but the function
        takes care that the reconnect procedure only runs once.

        :param node:
        :return:
        """
        with self._lock:
            node_id = node.node_id

            if node.node_id not in self._active_nodes:
                return False

            del self._active_nodes[node_id]

            try:
                tasks = self._scheduled_tasks[node_id]
                connection = self._connections[node_id]
            except KeyError:
                raise KeyError(f'node {node_id} does not exist, add it first')

            for task in tasks:
                task.cancel()

            connection.disconnect()
            self._event_dispatcher.fire_on_disconnect(node)
            self._scheduler.schedule(self._do_try_activate, start=time.time() + self.retry_interval, args=(node_id,))

    def _do_try_activate(self, node_id: str):
        logger.info('beginning activation routine for %s', node_id)

        with self._lock:
            try:
                node = self._nodes[node_id]
                connection = self._connections[node_id]
            except KeyError:
                logger.warning('inconsistent state for node %s, not connecting', node_id)
                return

        then = time.time()
        logger.debug('attempting to connect to node %s', node_id)
        connected = False
        try:
            if is_up(node):
                connection.connect()
                connected = connection.is_connected
        except Exception:
            pass
        logger.debug('connection attempt to node %s took %.2f s', node_id, time.time() - then)

        if not connected:
            self._scheduler.schedule(self._do_try_activate, start=time.time() + self.retry_interval, args=(node_id,))
            return

        logger.debug('connection attempt to %s, successful', node_id)
        with self._lock:
            self._active_nodes[node_id] = node

            tasks = self._scheduled_tasks[node_id]
            logger.info('re-scheduling %d tasks for node %s', len(tasks), node_id)
            for task in tasks:
                logger.debug('re-scheduling task %s', task.task)
                self._scheduler.schedule_task(task)

        self._event_dispatcher.fire_on_activate(node)

    def _do_exec_command(self, node_info: NodeInfo, command, callback: CommandCallback, listen=False):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('[%s] executing %s for node %s', threading.current_thread().name, command, node_info.node_id)

        try:
            with self._lock:
                try:
                    connection = self._connections[node_info.node_id]
                except KeyError:
                    logger.debug('connection for node %s was closed in the meantime', node_info.node_id)
                    # connection was closed in the meantime
                    return

            channel = connection.channel()
            channel.node_info = node_info
            channel.exec_command(command)

            if listen:
                collector = _NodeResultCollector(node_info, callback.on_result, aggregate=False,
                                                 closed_handler=self._on_node_disconnect)
            else:
                collector = _NodeResultCollector(node_info, callback.on_result, aggregate=True)

            self._event_loop.register(channel, collector)

        except (SSHException, socket.error) as e:
            logger.debug('error while executing command %s on node %s: %s', command, node_info.node_id, e)
            callback.on_exception(node_info, e)
            self._on_node_disconnect(node_info)
        except Exception as e:
            logger.exception('general exception while executing command %s', command)
            callback.on_exception(node_info, e)
