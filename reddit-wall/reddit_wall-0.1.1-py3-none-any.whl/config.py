"""Configuration module.

This module provides functions for finding, reading, and creating user
configuration files. It also provides an object, CONFIG, for easy access
to the loaded config.
"""

import os
import shutil
from configparser import ConfigParser

DEFAULT_CONFIG_FILE = "~/.config/reddit-wall.conf"

# FIXME: Add support for specifying config path as a command line argument
def create_config(config_file=None):
    """Read the program config file and create one if it doesn't exist.

    Parameters
    ----------
    config_file : string
        Path to the config file if not using the default.

     Returns
     -------
     parser : ConfigParser
        An instance of the program configuration.

    """

    default_config_path = os.path.expanduser(DEFAULT_CONFIG_FILE)
    if not config_file and not os.path.exists(default_config_path):
        shutil.copyfile("conf/reddit-wall.conf", default_config_path)

    parser = ConfigParser(allow_no_value=True)

    parser.read_file(open(default_config_path))
    if config_file:
        parser.read(config_file)

    return parser

CONFIG = create_config()
