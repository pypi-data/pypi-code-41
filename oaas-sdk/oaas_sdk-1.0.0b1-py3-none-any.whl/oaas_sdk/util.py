"""
Utility and helper methods
"""
import os

from oaas_sdk.objects import ConfigurationException

# we use ujson if available
try:
    import ujson as json
except ImportError:
    import json

# constants
_OAAS_WEBSERVICE_ROOT = 'oaas_webservice_root'
_USER = 'user'
_PASSWORD = 'pass'
UPDATE_FREQUENCY = 5
"""Frequency with which SDK will query the webservice for updated values."""


class _Configuration:
    """
    Configuration as specified in user's local config file at `$HOME/.oaas/sdk.json`
    """

    __SDK_CONFIG_FILE_LOCATION = "~/.oaas/sdk.json"

    def __init__(self):
        """
        Read configuration file and store values in object for easy retrieval
        """
        absolute_config_file_path: str = os.path.abspath(os.path.expanduser(_Configuration.__SDK_CONFIG_FILE_LOCATION))
        if not os.path.exists(absolute_config_file_path):
            raise ConfigurationException("Config file not found. Please create configuration file at: {}".format(absolute_config_file_path))

        with open(absolute_config_file_path, 'r') as config_file:
            config_json = config_file.read()
            config_dict = json.loads(config_json)

        if _OAAS_WEBSERVICE_ROOT not in config_dict:
            raise ConfigurationException("Configuration file must include {}".format(_OAAS_WEBSERVICE_ROOT))
        self.webservice_root = config_dict[_OAAS_WEBSERVICE_ROOT]

        if _USER not in config_dict:
            raise ConfigurationException("Configuration file must include {}".format(_USER))
        self.user = config_dict[_USER]

        if _PASSWORD not in config_dict:
            raise ConfigurationException("Configuration file must include {}".format(_PASSWORD))
        self.password = config_dict[_PASSWORD]


configuration = _Configuration()
"""Singleton configuration; this is the variable to import and use."""
