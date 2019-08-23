import time
import unittest
from collections import defaultdict
from unittest.mock import patch, MagicMock

from symmetry.api import NodeInfo, Telemetry
from symmetry.common.niossh import Result
from symmetry.telemetry.monitor import EventBasedClusterMonitor, TelemetryCommand

# mocked state
nodes = [
    NodeInfo('fake1', '127.0.0.1'),
    NodeInfo('fake2', '127.0.0.2'),
    NodeInfo('fake3', '127.0.0.3'),
]
active_nodes = [nodes[0], nodes[1]]


class FakeConnection:
    node: NodeInfo

    def __init__(self, node) -> None:
        super().__init__()
        self.node = node

    @property
    def is_connected(self):
        return self.node in active_nodes

    def connect(self):
        pass

    def disconnect(self):
        pass

    def channel(self):
        mock = MagicMock(name='Channel')
        mock.exec_command.side_effect = _exec_command
        return mock


def _create_connection(node):
    return FakeConnection(node)


def _is_up(node):
    if node in active_nodes:
        return True
    else:
        return False


def _register_channel(channel, callback):
    result = Result()
    result.stdout = ['42', 'OK']
    callback.on_result(channel, result)


def _exec_command(*args, **kwargs):
    pass


class TestTelemetryCommand(TelemetryCommand):
    metric = 'unittest'
    cmd = "fake-command"

    def __init__(self) -> None:
        super().__init__(self.cmd, self.to_data)

    def to_data(self, _: 'TelemetryCommand', node_info: NodeInfo, result) -> Telemetry:
        return Telemetry(self.metric, node_info, time.time(), 42)


class MonitorTest(unittest.TestCase):

    # FIXME: this test could probably make better use of mocking

    @patch('symmetry.telemetry.monitor.ChannelEventLoop.register')
    @patch('symmetry.telemetry.monitor.create_connection')
    @patch('symmetry.telemetry.monitor.is_up')
    def test_basic_integration_test(self, is_up, create_connection, register):
        is_up.side_effect = _is_up
        register.side_effect = _register_channel
        create_connection.side_effect = _create_connection

        telemetry = defaultdict(list)

        def on_data(command, data):
            telemetry[data.node].append(data)

        monitor = EventBasedClusterMonitor()
        monitor.add_data_listener(on_data)

        monitor.start()
        try:
            monitor.add_node(nodes[0])
            monitor.add_node(nodes[1])
            monitor.schedule(TestTelemetryCommand(), period=0.25)
            time.sleep(0.5)
            active_nodes.remove(nodes[0])
            monitor._on_node_disconnect(nodes[0])
            time.sleep(0.5)
        finally:
            monitor.stop()

        self.assertAlmostEqual(2, len(telemetry[nodes[0]]), delta=1)
        self.assertAlmostEqual(4, len(telemetry[nodes[1]]), delta=1)
        self.assertEqual(0, len(telemetry[nodes[2]]))
