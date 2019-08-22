#!/usr/bin/env python3
"""
Summary.

    Prints iam usernames from local awscli configuration.
    A usernames may be omitted from the output simply by
    listing them with a space between them after the call:

    .. code:: bash

        $ python3 iam_users.py default

Returns:

    Will return all iam usernames in the local configuration
    except the default user (username "default")

"""
import os
import inspect
from botocore.exceptions import ClientError, ProfileNotFound
from pyaws.session import client_wrapper as clientcreator
from pyaws.utils import stdout_message
from keyup.common import os_parityPath
from keyup.statics import local_config
from keyup import logger


try:
    from configparser import ConfigParser
except Exception:
    logger.exception('unable to import configParser library. Exit')
    raise e


def iam_users(profile):
    try:
        client = clientcreator('iam', profile=profile)
    except ClientError as e:
        logger.exception(
            "%s: IAM user or role not found (Code: %s Message: %s)" %
            (inspect.stack()[0][3], e.response['Error']['Code'],
             e.response['Error']['Message']))
        stdout_message('IAM user or role not found ({})'.format(profile), 'WARN')
    except ProfileNotFound:
        msg = (
            '%s: The profile (%s) was not found in your local config' %
            (inspect.stack()[0][3], profile))
        stdout_message(msg, 'FAIL')
        logger.warning(msg)
    return [x['UserName'] for x in client.list_users()['Users']]


def create_userlist(content, exclusions):
    """
    Summary:
        Return usernames from configParser object if not in
        the exclusion list

    Args:
        content (configParser object):  local awscli credentials file parsed content
        exclusions (list):  profilenames to be excluded from return

    Returns:
        list of profile names from localhost awscli configuration

    """
    return [x for x in content.sections() if x not in exclusions]


def temporary_profilenames(conf, exclusions=[]):
    """
    Summary:
        Return usernames from configParser object which
        represent temporary (iam role) credentials

    Args:
        :conf (str):  path to awscli credentials file
        :exclusions (list):  profilenames to be excluded from return

    Returns:
        temporary profile names (role names) from localhost awscli configuration
        TYPE: str

    """
    config = ConfigParser()

    try:
        if os.path.isfile(conf):
            config.read(conf)
    except Exception:
        logger.exception(f'{conf} configuration provided is not a filesystem object')

    for profile in config.sections():
        if ('aws_access_key_id' or 'aws_secret_access_key') in config[profile].keys():
            config.pop(profile)
    return [x for x in config.sections() if x not in exclusions]


def shared_credentials_location():
    """
    Summary:
        Discover alterate location for awscli shared credentials file

    Returns:
        TYPE: str, Full path of shared credentials file, if exists

    """
    if 'AWS_SHARED_CREDENTIALS_FILE' in os.environ:
        return os.environ['AWS_SHARED_CREDENTIALS_FILE']

    try:
        home = local_config['PROJECT']['HOME']
    except Exception as e:
        logger.critical(f'Problem extracting user home dir from local_config')
        raise e
    return os_parityPath(home + '/.aws/credentials')

5
def awscli_profiles(conf):
    """
    Summary.

        Returns IAM usernames from local awscli configuration

    """
    config = ConfigParser()

    try:
        if os.path.isfile(conf):
            config.read(conf)
    except Exception:
        logger.exception(f'{conf} configuration provided is not a filesystem object')

    for profile in config.sections():
        if 'role_arn' in config[profile].keys() or 'aws_security_token' in config[profile].keys():
            config.pop(profile)
    return config


def print_profiles(config, args):
    """Execution when no parameters provided"""
    try:
        print_array(config, args)
    except OSError as e:
        print('{}: OSError: {}'.format(inspect.stack(0)[3], e))
        return False
    return True


def local_profilenames(exceptions=[]):
    """

    """
    # globals
    home = os.environ.get('HOME')
    config_file = shared_credentials_location()

    modified_config = awscli_profiles(config_file)
    return create_userlist(modified_config, exceptions)
