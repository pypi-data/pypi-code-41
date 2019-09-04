import logging
import threading
import time
from datetime import datetime, timezone

import pymq

from symmetry.api import NodeInfo, Telemetry, NodeRemovedEvent, NodeManager, NodeCreatedEvent, NodeDisconnectedEvent, \
    NodeActivatedEvent
from symmetry.common.niossh import Result
from symmetry.telemetry.monitor import TelemetryCommand, EventBasedClusterMonitor, NodeStateListener
from symmetry.telemetry.power import PowerMonitor

logger = logging.getLogger(__name__)


class RedisTelemetryDataPublisher(NodeStateListener):

    def __init__(self, redis_client) -> None:
        super().__init__()
        self.redis_client = redis_client

    def on_data(self, command: TelemetryCommand, data: Telemetry):
        if data.service:
            topic = 'telemetry:%s:%s:%s' % (data.metric, data.node.node_id, data.service)
        else:
            topic = 'telemetry:%s:%s' % (data.metric, data.node.node_id)
        value = '%s %s' % (data.time, data.value)

        self.redis_client.publish(topic, value)

    def on_disconnect(self, node_info: NodeInfo):
        topic = 'telemetry:status:%s' % node_info.node_id
        value = '%s false' % time.time()

        self.redis_client.publish(topic, value)

    def on_activate(self, node_info: NodeInfo):
        topic = 'telemetry:status:%s' % node_info.node_id
        value = '%s true' % time.time()

        self.redis_client.publish(topic, value)


class TelemetryLogger(NodeStateListener):

    def __init__(self, level=logging.DEBUG, log=logger) -> None:
        super().__init__()
        self.level = level
        self.log = log

    def on_data(self, cmd: TelemetryCommand, data: Telemetry):
        self.log.log(self.level, '[%s] %s, %s, %s',
                     threading.current_thread().name, data.node.node_id, cmd.__class__.__name__, data.value)

    def on_error(self, cmd: TelemetryCommand, node_info: NodeInfo, err: Exception):
        msg = '[{thread}] error executing {cmd} on node {node}: {err}'.format(
            thread=threading.current_thread().name,
            cmd=cmd.__class__.__name__,
            node=node_info.node_id,
            err=err
        )
        self.log.error(msg, exc_info=err)

    def on_disconnect(self, node_info: NodeInfo):
        self.log.log(self.level, '[%s] disconnect %s', threading.current_thread().name, node_info.node_id)

    def on_activate(self, node_info: NodeInfo):
        self.log.log(self.level, '[%s] activate %s', threading.current_thread().name, node_info.node_id)


class NodeStateEventbusPublisher(NodeStateListener):

    def on_disconnect(self, node_info: NodeInfo):
        pymq.publish(NodeDisconnectedEvent(node_info.node_id))

    def on_activate(self, node_info: NodeInfo):
        pymq.publish(NodeActivatedEvent(node_info.node_id))


class CpuFrequencyCommand(TelemetryCommand):
    metric = 'freq'
    cmd = "cat /proc/cpuinfo | grep MHz | cut -d' ' -f3 | xargs; date +%s.%N"

    def __init__(self) -> None:
        super().__init__(self.cmd, self.to_data)

    def to_data(self, _: 'TelemetryCommand', node_info: NodeInfo, result: Result) -> Telemetry:
        lines = result.stdout
        value = sum([float(v) for v in lines[0].split(" ") if v])
        t = float(lines[1])

        return Telemetry(self.metric, node_info, t, value)


class LoadCommand(TelemetryCommand):
    cmd = "cat /proc/loadavg; date +%s.%N"

    def __init__(self) -> None:
        super().__init__(self.cmd, self.to_data)

    def to_data(self, _: 'TelemetryCommand', node_info: NodeInfo, result: Result):
        lines = result.stdout

        values = lines[0].split(' ')
        t = float(lines[1])

        return [
            Telemetry('load_1', node_info, t, float(values[0])),
            Telemetry('load_5', node_info, t, float(values[1])),
            # Telemetry('load_15', node_info, t, float(values[2]))
        ]


class CpuUtilCommand(TelemetryCommand):
    metric = 'cpu'
    cmd = "cat <(grep 'cpu ' /proc/stat) <(sleep 0.25 && grep 'cpu ' /proc/stat)" \
          " | awk -v RS='' '{print ($13-$2+$15-$4)*100/($13-$2+$15-$4+$16-$5)}'; date +%s.%N"

    def __init__(self) -> None:
        super().__init__(self.cmd, self.to_data)

    def to_data(self, _: 'TelemetryCommand', node_info: NodeInfo, result: Result) -> Telemetry:
        lines = result.stdout
        return Telemetry(self.metric, node_info, float(lines[1]), float(lines[0]))


class AccessLoggingCommand(TelemetryCommand):
    """
    filters the access log like so:
    time;requestname;requesttime
    """
    metric = 'rtt'
    cmd = "tail -F /var/log/nginx/apm_access.log | grep --line-buffered 'status=200' |" \
          "sed -u '" \
          's/^\("[^"]*"\).*request=\("[^"]*"\).*=\([0-9.]*\)$/\\1;\\2;\\3/' \
          "'"

    def __init__(self) -> None:
        super().__init__(self.cmd, self.to_data)

    @staticmethod
    def extract_service(http_request):
        return http_request.split()[1].split("/")[1]

    @staticmethod
    def convert_timestamp(timestamp):
        utc_time = datetime.strptime(timestamp, '"%d/%b/%Y:%H:%M:%S %z"')
        epoch_time = (utc_time - datetime(1970, 1, 1).replace(tzinfo=timezone.utc)).total_seconds()
        return epoch_time

    def to_data(self, _: 'TelemetryCommand', node_info: NodeInfo, result: Result) -> Telemetry:
        triple = result.stdout[0].split(';')
        log_time = self.convert_timestamp(triple[0])
        service = self.extract_service(triple[1])
        req_dur = triple[2]

        return Telemetry(self.metric, node_info, log_time, req_dur, service)


class TelemetryDaemon:
    monitor: EventBasedClusterMonitor
    node_manager: NodeManager

    def __init__(self, node_manager, redis_client, args=None) -> None:
        super().__init__()
        self.node_manager = node_manager
        self.rds = redis_client
        self.args = args or dict()

        self.pmon = None
        self.pmon_thread = None

        pymq.subscribe(self._on_node_removed)
        pymq.subscribe(self._on_node_created)

    def start(self):
        # TODO: enable power monitor once merged
        if not self.args.get('power_disable'):
            self.pmon = PowerMonitor(self.rds, interval=self.args.get('power_interval'))
            self.pmon_thread = threading.Thread(target=self.pmon.run, name='power-monitor')
            self.pmon_thread.start()

        self.monitor = self.init_cluster_monitor()
        logger.info('starting monitor')
        self.monitor.start()

    def _on_node_removed(self, event: NodeRemovedEvent):
        self.monitor.remove_node(event.node_id)

    def _on_node_created(self, event: NodeCreatedEvent):
        node_info = self.node_manager.get_node(event.node_id)
        self.monitor.add_node(node_info)

    def init_cluster_monitor(self):
        monitor = EventBasedClusterMonitor()

        for node in self.node_manager.get_nodes():
            logger.debug('adding cluster node to monitor %s', node)
            monitor.add_node(node)

        if logger.isEnabledFor(logging.DEBUG):
            telemetry_logger = TelemetryLogger()
            monitor.add_data_listener(telemetry_logger.on_data)
            monitor.add_error_listener(telemetry_logger.on_error)
            monitor.add_node_state_listener(telemetry_logger)

        redis_publisher = RedisTelemetryDataPublisher(self.rds)

        monitor.add_data_listener(redis_publisher.on_data)
        monitor.add_node_state_listener(redis_publisher)
        monitor.add_node_state_listener(NodeStateEventbusPublisher())
        monitor.schedule(CpuUtilCommand(), period=self.args.get('agent_interval'))
        monitor.schedule(CpuFrequencyCommand(), period=self.args.get('agent_interval'))
        monitor.schedule(LoadCommand(), period=self.args.get('agent_interval'))

        # TODO: is it intended behaviour, that listening can only be done _after_ adding nodes?
        # monitor.listen(AccessLoggingCommand())

        return monitor

    def stop(self):
        if self.pmon:
            logger.debug('stopping power monitor')
            self.pmon.cancel()
            self.pmon_thread.join()

        logger.debug('stopping cluster monitor')
        self.monitor.stop()

        logger.debug('telemetry daemon has stopped')
