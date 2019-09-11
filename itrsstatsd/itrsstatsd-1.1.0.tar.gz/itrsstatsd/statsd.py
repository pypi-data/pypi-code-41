# -*- coding: utf-8 -*-

import os
from .api import Api
from .senders import StatsdMetricsSender
from .channels import UdpChannel, TcpChannel, StdoutChannel

DEFAULT_STATSD_SERVER = 'localhost'
DEFAULT_STATSD_PORT = 8125
PROTO_TCP = 'tcp'
PROTO_UDP = 'udp'

environment_dimensions_kubernetes = {
    'NAMESPACE': 'namespace',
    'CONTAINER_NAME': 'container_name',
    'POD_NAME': 'pod_name',
    'HOSTNAME': 'hostname'
}

environment_dimensions_default = {
    'HOSTNAME': 'hostname',
    'APP_NAME': 'app_name'
}


def build_statsd(**kwargs):
    """Build a statsd API client.

    :param kwargs: (optional) If 'hostname' and/or 'port' are supplied they specify the statsd server hostname and port
        respectively, else the environment variables 'STATSD_SERVER' and/or 'STATSD_PORT' are used. If none are present
        then it is assumed the statsd server is running on 'localhost' on port 8125.
        If 'protocol' is supplied, it will override the default of UDP. Valid values are 'tcp' and 'udp'.
    :return: :class:`Api`
    :rtype: itrsstatsd.Api
    :raises: ValueError if unknown protocol specified
    """

    hostname = kwargs.get('hostname', os.environ.get('STATSD_SERVER', DEFAULT_STATSD_SERVER))
    port = int(kwargs.get('port', os.environ.get('STATSD_PORT', DEFAULT_STATSD_PORT)))
    protocol = kwargs.get('protocol', PROTO_UDP)

    if PROTO_TCP == protocol:
        channel = TcpChannel(hostname, port)
    elif PROTO_UDP == protocol:
        channel = UdpChannel(hostname, port)
    else:
        raise ValueError('Unknown protocol: ' + protocol)

    return add_default_env_dimensions(Api(StatsdMetricsSender(channel)))


def add_default_env_dimensions(api: Api):
    pod_name = os.environ.get('POD_NAME', None)
    if pod_name is not None:
        dims = environment_dimensions_kubernetes
    else:
        dims = environment_dimensions_default

    for env_name, dimension_name in dims.items():
        env_value = os.environ.get(env_name, None)
        if env_value is not None:
            api.default_dimension(dimension_name, env_value)

    return api


def build_test_statsd():
    """Build a test statsd API client.

    A test statsd API client simply outputs statsd packets to stdout rather than to a statsd server.

    :return: :class:`Api`
    :rtype: itrsstatsd.Api
    """

    return add_default_env_dimensions(Api(StatsdMetricsSender(StdoutChannel())))
