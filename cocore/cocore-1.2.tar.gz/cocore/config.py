import base64
from configparser import ConfigParser
import os

from future import standard_library
standard_library.install_aliases()
from future.builtins import str

def Config(conf_path='etl.cfg'):
    """Reads config file and returns a dictionary of config objects.

    :param conf_path: Absolute path to configuration file.
    :return: Dictionary with configuration arguments and values
    """
    config = ConfigParser()
    config.read(conf_path)
    dictionary = {}
    for section in config.sections():
        dictionary[section] = {}
        for option in config.options(section):
            val = config.get(section, option)
            if str(option).lower() in ('pwd', 'password'):
                val = str(base64.b64decode(val), 'utf-8')
            dictionary[section][option] = val
    return dictionary
