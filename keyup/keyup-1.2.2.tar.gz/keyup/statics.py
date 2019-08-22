"""
Summary.

    keyup Project-level Defaults and Settings

    - **Local Default Settings**: Local defaults for your specific installation are derived from settings found in:

    .. code-block:: bash

        ~/.config/keyup/config.json

Module Attributes:
    - user_home (TYPE str):
        $HOME environment variable, present for most Unix and Unix-like POSIX systems
    - config_dir (TYPE str):
        directory name default for stsaval config files (.stsaval)
    - config_path (TYPE str):
        default for stsaval config files, includes config_dir (~/.stsaval)
    - key_deprecation (TYPE str):
        Deprecation logic that keyup uses when 2 keys exist for a user.

        2 values possible:

            - 'AGE':  keyup deprecates based on age, replacing the oldest key
            - 'AWSCLI':  keyup replaces keys currently in the local awscli config

"""
import json
import os
import platform
import inspect
import logging
from keyup._version import __version__

logger = logging.getLogger(__version__)
logger.setLevel(logging.INFO)


# --  project-level DEFAULTS  ------------------------------------------------


def get_os(detailed=False):
    """
    Summary:
        Retrieve local operating system environment characteristics
    Args:
        :user (str): USERNAME, only required when run on windows os
    Returns:
        TYPE: dict object containing key, value pairs describing
        os information
    """
    try:

        os_type = platform.system()

        if os_type == 'Linux':
            os_detail = platform.uname()
            distribution = platform.linux_distribution()
            HOME = os.environ['HOME']
            username = os.getenv('USER')
        elif os_type == 'Windows':
            username = os.getenv('username')
            HOME = 'C:\\Users\\' + username
        elif os_type == 'Java':
            logger.warning('Unsupported OS. No information')
    except OSError as e:
        raise e
    except Exception as e:
        logger.exception(
            '%s: problem determining local os environment %s' %
            (inspect.stack()[0][3], str(e))
            )
    if detailed and os_type == 'Linux':
        return {
                'os_type': os_type,
                'os_detail': os_detail,
                'linux_distribution': distribution,
                'HOME': HOME
            }
    elif detailed and os_type == 'Windows':
        return {
                'os_type': os_type,
                'platform': platform,
                'HOME': HOME
            }
    elif not detailed:
        return {'os_type': os_type}


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


def os_parityPath(path):
    """
    Converts unix paths to correct windows equivalents.
    Unix native paths remain unchanged (no effect)
    """
    path = os.path.normpath(os.path.expanduser(path))
    if path.startswith('\\'):
        return 'C:' + path
    return path


try:

    env_info = get_os(detailed=True)
    OS = env_info['os_type']
    user_home = env_info['HOME']

except KeyError as e:
    logger.critical(
        '%s: %s variable is required and not found in the environment' %
        (inspect.stack()[0][3], str(e)))
    raise e
else:
    # local vars -- this section executes as default; if windows, execute diff
    # section with appropriate pathnames

    # project
    PACKAGE = 'keyup'
    LICENSE = 'GPL v3'
    LICENSE_DESC = 'General Public License v3'
    version = __version__

    # config parameters
    CONFIG_SCRIPT = 'keyconfig'         # console script to access config file
    config_dir = '.config'
    config_subdir = PACKAGE
    config_filename = 'config.json'
    config_path = user_home + '/' + config_dir + '/' + config_subdir + '/' + config_filename

    # access key parameters
    keyage_min = 1                      # days
    keyage_max = 30                     # days
    keyage_limit = 365
    keyage_warning = 2                  # warn when 2 days till expiration
    key_deprecation = 'AGE'             # 'AWSCLI' || 'AGE'
    rotation_delay = 9                  # seconds

    # logging parameters
    enable_logging = False
    log_mode = 'FILE'
    log_filename = 'keyup.log'
    log_dir = user_home + '/' + 'logs'
    log_path = log_dir + '/' + log_filename

    # key backup parameters
    backup_enable = False
    backup_location = user_home + '/' + 'Backup' + '/' + 'keysets'

    if OS == 'Windows':
        config_path = os_parityPath(config_path)
        log_path = os_parityPath(log_path)
        backup_location = os_parityPath(backup_location)

    seed_config = {
        "PROJECT": {
            "PACKAGE": PACKAGE,
            "CONFIG_VERSION": version,
            "CONFIG_DATE": "",
            "HOME": user_home,
            "CONFIG_FILENAME": config_filename,
            "CONFIG_DIR": config_dir,
            "CONFIG_SUBDIR": config_subdir,
            "CONFIG_PATH": config_path
        },
        "TEMP_CREDENTIALS": {
            "PROFILE_NAMES": []
        },
        "LOGGING": {
            "ENABLE_LOGGING": enable_logging,
            "LOG_FILENAME": log_filename,
            "LOG_PATH": log_path,
            "LOG_MODE": log_mode,
            "SYSLOG_FILE": False
        },
        "KEY_METADATA": {
            "KEYAGE_MAX_DAYS": keyage_max,
            "KEYAGE_MIN_DAYS": keyage_min,
            "KEYAGE_MAX_LIMIT": keyage_limit,
            "KEYAGE_WARNING": keyage_warning,
            "KEY_DEPRECATION": key_deprecation,
            "KEY_ENABLE_DELAY": rotation_delay
        },
        "KEY_BACKUP": {
            "BACKUP_ENABLE": backup_enable,
            "BACKUP_LOCATION": backup_location
        }
    }

try:
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
        os.chmod(log_dir, 0o755)
    if os.path.exists(config_path):
        # parse config file
        local_config = read_local_config(cfg=config_path)
        # fail to read, set to default config
        if not local_config:
            local_config = seed_config
    else:
        local_config = seed_config

except KeyError:
    local_config = seed_config
except OSError as e:
    logger.exception(
        '%s: Error when attempting to access or create local log and config %s' %
        (inspect.stack()[0][3], str(e))
    )
    raise e
