"""
Command-line Interface (CLI) Utilities Module

Module Functions:
    - bool_assignment:
        set bool depending up user answer from stdin
    - config_init:
        Initializes config file if none exists
    - debug_mode:
        Provide additional log output for debugging
    - read_local_config:
        parse local config file
"""
import sys
import os
import json
import platform
import datetime
import re
import logging
import inspect
from libtools.js import export_iterobject
from keyup.colors import Colors
from keyup import __version__

# globals
MODULE_VERSION = '1.14'

try:
    from keyup import logger
except Exception:
    logger = logging.getLogger(__version__)
    logger.setLevel(logging.INFO)


def bool_assignment(arg, patterns=None):
    """
    Summary:
        Enforces correct bool argment assignment
    Arg:
        :arg (*): arg which must be interpreted as either bool True or False
    Returns:
        bool assignment | TYPE:  bool
    """
    arg = str(arg)    # only eval type str
    try:
        if patterns is None:
            patterns = (
                (re.compile(r'^(true|false)$', flags=re.IGNORECASE), lambda x: x.lower() == 'true'),
                (re.compile(r'^(yes|no)$', flags=re.IGNORECASE), lambda x: x.lower() == 'yes'),
                (re.compile(r'^(y|n)$', flags=re.IGNORECASE), lambda x: x.lower() == 'y')
            )
        if not arg:
            return ''    # default selected
        else:
            for pattern, func in patterns:
                if pattern.match(arg):
                    return func(arg)
    except Exception as e:
        raise e


def config_init(config_file, json_config_obj, config_dirname=None):
    """
    Summary:
        Creates local config from JSON seed template
    Args:
        :config_file (str): filesystem object containing json dict of config values
        :json_config_obj (json):  data to be written to config_file
        :config_dirname (str):  dir name containing config_file
    Returns:
        TYPE: bool, Success | Failure
    """
    HOME = os.environ['HOME']
    # client config dir
    if config_dirname:
        dir_path = HOME + '/' + config_dirname
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
            os.chmod(dir_path, 0o755)
    else:
        dir_path = HOME
    # client config file
    r = export_iterobject(
            dict_obj=json_config_obj,
            filename=dir_path + '/' + config_file
        )
    return r


def debug_mode(header, data_object, debug=False, halt=False):
    """ debug output """
    if debug:
        print('\n  ' + str(header) + '\n')
        try:
            export_iterobject(data_object)
        except Exception:
            print(data_object)
        if halt:
            sys.exit(0)
    return True


def import_file_object(filename):
    """
    Summary:
        Imports block filesystem object
    Args:
        :filename (str): block filesystem object
    Returns:
        dictionary obj (valid json file), file data object
    """
    try:
        handle = open(filename, 'r')
        file_obj = handle.read()
        dict_obj = json.loads(file_obj)

    except OSError as e:
        logger.critical(
            'import_file_object: %s error opening %s' % (str(e), str(filename))
        )
        raise e
    except ValueError:
        logger.info(
            '%s: import_file_object: %s not json. file object returned' %
            (inspect.stack()[0][3], str(filename))
        )
        return file_obj    # reg file, not valid json
    return dict_obj


def read_local_config(cfg):
    """ Parses local config file for override values

    Args:
        :local_file (str):  filename of local config file

    Returns:
        dict object of values contained in local config file
    """
    try:
        if os.path.exists(cfg):
            config = import_file_object(cfg)
            return config
        else:
            logger.warning(
                '%s: local config file (%s) not found, cannot be read' %
                (inspect.stack()[0][3], str(cfg)))
    except OSError as e:
        logger.warning(
            'import_file_object: %s error opening %s' % (str(e), str(cfg))
        )
    return {}
