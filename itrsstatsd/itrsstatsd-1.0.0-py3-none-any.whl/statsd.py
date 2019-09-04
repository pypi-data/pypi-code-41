# -*- coding: utf-8 -*-

import os
from .api import Api
from .senders import StatsdMetricsSender
from .channels import UdpChannel, StdoutChannel

DEFAULT_STATSD_SERVER = 'localhost'
DEFAULT_STATSD_PORT = 8125

environment_dimensions = {
    'NAMESPACE': 'namespace',
    'CONTAINER_NAME': 'container_name',
    'POD_NAME': 'pod_name',
    'HOSTNAME': 'hostname'
}


def build_statsd(**kwargs):
    """Build a statsd API client.

    :param kwargs: (optional) If 'hostname' and/or 'port' are supplied they specify the statsd server hostname and port
        respectively, else the environment variables 'STATSD_SERVER' and/or 'STATSD_PORT' are used. If none are present
        then it is assumed the statsd server is running on 'localhost' on port 8125.
    :return: :class:`Api`
    :rtype: itrsstatsd.Api
    """

    hostname = kwargs.get('hostname', os.environ.get('STATSD_SERVER', DEFAULT_STATSD_SERVER))
    port = int(kwargs.get('port', os.environ.get('STATSD_PORT', DEFAULT_STATSD_PORT)))
    return add_default_env_dimensions(Api(StatsdMetricsSender(UdpChannel(hostname, port))))


def add_default_env_dimensions(api: Api):
    for env_name, dimension_name in environment_dimensions.items():
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
