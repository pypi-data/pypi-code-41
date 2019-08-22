"""
Summary:
    - Mapping Module
    - maps profile names from local awscli to iam usernames in AWS Account

"""

import sys
import inspect
from botocore.exceptions import ClientError
from pyaws.session import boto3_session
from libtools import stdout_message
from libtools import Colors
from keyup.iam_operations import local_profilenames
from keyup import logger


try:
    from keyup.oscodes_unix import exit_codes
    os_type = 'Linux'
    splitchar = '/'                             # character for splitting paths (linux)
    text = Colors.BRIGHT_CYAN
except Exception:
    from keyup.oscodes_win import exit_codes    # non-specific os-safe codes
    os_type = 'Windows'
    splitchar = '\\'                            # character for splitting paths (windows)
    text = Colors.CYAN


def map_iam_username(username, profilename):
    """
    Summary:
        Triangulates if provided username is a profile name from local
        awscli configuration or an IAM username from AWS

    Returns:
        IAM username (str)

    """
    # search for username in profilenames in case not an iam username
    if username in local_profilenames():
        return map_identity(username)[0] or username

    client = boto3_session(service='iam', profile=profilename)
    r = client.list_users()

    try:
        if username in [x['UserName'] for x in r['Users']]:
            return username
    except KeyError:
        logger.warning(f'Profilename given ({profilename}) not found in local awscli')
        var = Colors.RED + username + Colors.RESET
        msg = f'Provided --username value {var} not a valid awscli profilename or iam username'
        stdout_message(message=msg, prefix='WARN')
        sys.exit(exit_codes['E_MISC']['Code'])


def map_identity(profile):
    """
    Summary:
        retrieves iam user info for profiles in awscli config
    Args:
        :user (str): string, local profile user from which the current
           boto3 session object created
    Returns:
        :iam_user (str): AWS iam user corresponding to the provided
           profile user in local config
    """
    try:
        sts_client = boto3_session(service='sts', profile=profile)
        r = sts_client.get_caller_identity()
        iam_user = r['Arn'].split('/')[1]
        account = r['Account']
        logger.info(
            '%s: profile %s mapped to iam_user: %s' %
            (inspect.stack()[0][3], profile, iam_user)
            )
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidClientTokenId':
            return None, None
        else:
            logger.warning(
                '%s: Inadequate User permissions (Code: %s Message: %s)' %
                (inspect.stack()[0][3], e.response['Error']['Code'],
                 e.response['Error']['Message']))
            raise e
    return iam_user, account
