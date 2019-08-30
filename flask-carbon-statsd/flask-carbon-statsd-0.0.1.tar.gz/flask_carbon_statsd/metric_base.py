import time
import socket
import platform
from statsd import StatsClient

class MetricBase(object):
    def __init__(self, host='localhost', port=8125, environment="dev"):
        self.hostname = self.get_reversed_hostname()
        self.statsd_host = host
        self.statsd_port = port
        self.measurement = None
        self.environment = environment

    def connect(self):
        return StatsClient(host=self.statsd_host,
                           port=self.statsd_port)


    def get_reversed_hostname(self):
        hostname = platform.node() or socket.gethostname()
        hostname_domain_components = hostname.split('.')
        hostname_domain_components.reverse()
        return '.'.join(hostname_domain_components)

    def mk_metric(self, metric, *tags):
        return '.'.join([metric] + list(map(str, list(tags))))
