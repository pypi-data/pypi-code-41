"""
Common Functionality (Utilities) Module

Module Functions:
    - awscli_defaults:
        determine awscli config file locations on localhost
    - import_file_object:
        import text filesystem object and convert to object
    - export_iterobject:
        write a json object to a filesystem object
    - ostype:
        Retrieve localhost os type, ancillary environment specifics
    - read_local_config:
        parse local config file
    - config_init:
        Initializes config file where none exists
"""
import sys
import os
import json
import platform
import datetime
import re
import logging
import inspect
import distro
from libtools.js import export_iterobject
from keyup.colors import Colors
from keyup import __version__


try:
    from keyup import logger
except Exception:
    logger = logging.getLogger(__version__)
    logger.setLevel(logging.INFO)


def _logging_enabled():
    """
    Test to determine if host system logging enabled; effective Redhat or Debian Linux
    """
    if any(os.path.exists(os.path.join('/var/log', x)) for x in ['syslog', 'messages']):
        return True
    return False


def convert_strtime_datetime(dt_str):
    """ Converts datetime isoformat string to datetime (dt) object

    Args:
        :dt_str (str): input string in '2017-12-30T18:48:00.353Z' form
         or similar
    Returns:
        TYPE:  datetime object
    """
    dt, _, us = dt_str.partition(".")
    dt = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
    us = int(us.rstrip("Z"), 10)
    return dt + datetime.timedelta(microseconds=us)


def convert_timedelta(duration):
    """
    Summary:
        Convert duration into component time units
    Args:
        :duration (datetime.timedelta): time duration to convert
    Returns:
        days, hours, minutes, seconds | TYPE: tuple (integers)
    """
    days, seconds = duration.days, duration.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return days, hours, minutes, seconds


def convert_dt_time(duration, return_iter=False):
    """
    Summary:
        convert timedelta objects to human readable output
    Args:
        :duration (datetime.timedelta): time duration to convert
        :return_iter (tuple):  tuple containing time sequence
    Returns:
        days, hours, minutes, seconds | TYPE: tuple (integers), OR
        human readable, notated units | TYPE: string
    """
    try:
        days, hours, minutes, seconds = convert_timedelta(duration)
        if return_iter:
            return days, hours, minutes, seconds
        # string format conversions
        if days > 0:
            format_string = (
                '{} day{}, {} hour{}'.format(
                 days, 's' if days != 1 else '', hours, 's' if hours != 1 else ''))
        elif hours > 1:
            format_string = (
                '{} hour{}, {} minute{}'.format(
                 hours, 's' if hours != 1 else '', minutes, 's' if minutes != 1 else ''))
        else:
            format_string = (
                '{} minute{}, {} sec{}'.format(
                 minutes, 's' if minutes != 1 else '', seconds, 's' if seconds != 1 else ''))
    except AttributeError as e:
        logger.exception(
            '%s: Type mismatch when converting timedelta objects (Code: %s)' %
            (inspect.stack()[0][3], str(e)))
    except Exception as e:
        logger.exception(
            '%s: Unknown error when converting datetime objects (Code: %s)' %
            (inspect.stack()[0][3], str(e)))
    return format_string


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


def awscli_defaults(os_type=None):
    """
    Summary:
        Parse, update local awscli config credentials
    Args:
        :user (str):  USERNAME, only required when run on windows os
    Returns:
        TYPE: dict object containing key, value pairs describing
        os information
    """

    try:
        if os_type is None:
            os_type = platform.system()

        if os_type == 'Linux':
            HOME = os.environ['HOME']
            awscli_credentials = HOME + '/.aws/credentials'
            awscli_config = HOME + '/.aws/config'
        elif os_type == 'Windows':
            username = os.getenv('username')
            awscli_credentials = 'C:\\Users\\' + username + '\\.aws\\credentials'
            awscli_config = 'C:\\Users\\' + username + '\\.aws\\config'
        elif os_type == 'Java':
            logger.warning('Unsupported OS. No information')
            HOME = os.environ['HOME']
            awscli_credentials = HOME + '/.aws/credentials'
            awscli_config = HOME + '/.aws/config'
        alt_credentials = os.getenv('AWS_SHARED_CREDENTIALS_FILE')
    except OSError as e:
        logger.exception(
            '%s: problem determining local os environment %s' %
            (inspect.stack()[0][3], str(e))
            )
        raise e
    return {
                'awscli_defaults': {
                    'awscli_credentials': awscli_credentials,
                    'awscli_config': awscli_config,
                    'alt_credentials': alt_credentials
                }
            }


def os_parityPath(path):
    """
    Converts unix paths to correct windows equivalents.
    Unix native paths remain unchanged (no effect)
    """
    path = os.path.normpath(os.path.expanduser(path))
    if path.startswith('\\'):
        return 'C:' + path
    return path


def distrotype():
    """
    Returns:
        rhel | debian | None, TYPE: str, (Nonetype)
    """
    for os in ['rhel', 'debian']:
        if re.search(os, distro.like()):
            return os
    return None

def syslog_enabled(system=distrotype()):
    """
        Determines which system logger is present and working

    Returns:
        True | False, TYPE: bool
    """
    logmap = {
        "amzn": "/var/log/messages",
        "debian": "/var/log/syslog",
        "rhel": "/var/log/messages"
    }

    try:
        return os.path.exists(logmap[system])
    except OSError:
        return True
