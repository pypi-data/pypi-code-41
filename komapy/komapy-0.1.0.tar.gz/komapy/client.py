"""
KomaPy data fetcher and reader.
"""

import json
from six.moves.urllib.request import urlopen
from six.moves.urllib.parse import urlencode

import bmaclient

from . import processing
from . import exceptions
from .settings import app_settings

__all__ = [
    'set_api_key',
    'set_access_token',
    'set_api_host',
    'fetch_bma_as_dictionary',
    'fetch_bma_as_dataframe',
    'fetch_url_as_dictionary',
    'fetch_url_as_dataframe',
]


def set_api_key(key):
    """
    Set BMA API key to enable accessing the API.
    """
    app_settings.api_key = key


def set_access_token(token):
    """
    Set BMA access token to enable accessing the API.
    """
    app_settings.access_token = token


def set_timezone(name):
    """
    Set app timezone setting.
    """
    app_settings.time_zone = name


def set_api_host(name):
    """
    Override BMA API default host.
    """
    app_settings.host = name


def fetch_bma_as_dictionary(name, params=None):
    """Make a request to the BMA API and return data as Python dictionary."""
    api = bmaclient.MonitoringAPI(
        api_key=app_settings.api_key,
        access_token=app_settings.access_token)
    if app_settings.host:
        api.host = app_settings.host

    method = api.get_fetch_method(name)
    if not method:
        raise exceptions.ChartError('Unknown parameter name {}'.format(name))
    query_params = params or {}
    return method(**query_params)


def fetch_bma_as_dataframe(name, params=None):
    """Make a request to the BMA API and return data as Pandas DataFrame."""
    response = fetch_bma_as_dictionary(name, params)
    return processing.dataframe_from_dictionary(response)


def fetch_url_as_dictionary(url, params=None):
    """Make a request to the URL and return data as Python dictionary."""
    full_query_params = '?{}'.format(urlencode(params)) if params else ''
    full_url_with_params = '{url}{query_params}'.format(
        url=url,
        query_params=full_query_params
    )

    with urlopen(full_url_with_params) as content:
        data = json.loads(content.read().decode('utf-8'))

    return data


def fetch_url_as_dataframe(url, params=None):
    """Make a request to the URL and return data as Pandas DataFrame."""
    response = fetch_url_as_dictionary(url, params)
    return processing.dataframe_from_dictionary(response)
