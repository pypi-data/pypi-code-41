"""
Summary.
    List iam keyset operations (read-only)

"""

import sys
import inspect
from botocore.exceptions import ClientError
from pyaws.session import boto3_session
from libtools import stdout_message
from keyup.vault import _display_keylist_header, _display_keylist_detail, _logging
from keyup.variables import bcy, cyn, rd, rst, bd, bdwt
from keyup import logger

try:
    from keyup.oscodes_unix import exit_codes
    os_type = 'Linux'
    splitchar = '/'                             # character for splitting paths (linux)
    text = bcy
except Exception:
    from keyup.oscodes_win import exit_codes    # non-specific os-safe codes
    os_type = 'Windows'
    splitchar = '\\'                            # character for splitting paths (windows)
    text = cyn


def query_keyinfo(account, profile, surrogate='', quiet=False):
    """
    Summary.
        boto3 client instantiation and error handling

    Args:
        :account (str): AWS account number
        :profile (str): name of the iam user for which we are interrogating keys
        :surrogate (str): name of profile user used to execute key operations
            in place of the profile user
        :quiet (bool): No output to stdout (True) | Show output (False)

    Returns:
        boto3 response, TYPE: dict

    """
    client = boto3_session(service='iam', profile=profile)

    try:
        if surrogate:
            r = client.list_access_keys(UserName=surrogate)
        else:
            r = client.list_access_keys()
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied' and surrogate:
            stdout_message(
                ('User %s has inadequate permissions for key operations\n\t     on user %s - Exit [Code: %d]' %
                 (profile, surrogate, exit_codes['EX_NOPERM']['Code'])),
                prefix='PERM', severity='WARNING'
                )
            logger.warning(exit_codes['EX_NOPERM']['Reason'])
            sys.exit(exit_codes['EX_NOPERM']['Code'])

        elif e.response['Error']['Code'] == 'AccessDenied':
            stdout_message(
                ('%s: User %s has inadequate permissions to conduct key operations. Exit [Code: %d]'
                 % (inspect.stack()[0][3], profile, exit_codes['EX_NOPERM']['Code'])),
                prefix='AUTH', severity='WARNING')
            logger.warning(exit_codes['EX_NOPERM']['Reason'])
            sys.exit(exit_codes['EX_NOPERM']['Code'])

        elif e.response['Error']['Code'] == 'NoSuchEntity':
            tab = '\n\t'.expandtabs(12)
            user = rd + bd + (surrogate if surrogate else profile) + rst
            stdout_message(
                (
                    'User %s does not exist in local awscli profiles %s for AWS Account %s [Code: %d]'
                    % (user, tab, bdwt + account + rst, exit_codes['EX_AWSCLI']['Code'])
                ),
                prefix='USER',
                severity='WARNING'
            )
            logger.warning(exit_codes['EX_AWSCLI']['Reason'])
            sys.exit(exit_codes['EX_AWSCLI']['Code'])

        else:
            logger.warning(
                '%s: Inadequate User permissions (Code: %s Message: %s)' %
                (inspect.stack()[0][3], e.response['Error']['Code'],
                 e.response['Error']['Message']))
            raise e
    return r['AccessKeyMetadata'], r['ResponseMetadata']['HTTPStatusCode']


def list_keys(account, profile, iam_user, surrogate='', stage=None, quiet=False):
    """
    Summary.
        Displays iam user available access keys

    Args:
        :account (str): AWS account number
        :profile (str): name of the iam user for which we are interrogating keys
        :iam_user (str): name of the iam user which corresponds to profile name
            from local awscli configuration
        :surrogate (str): name of profile user used to execute key operations
            in place of the profile user
        :stage (str): stage of key rotation; ie, either BEFORE | AFTER rotation
        :quiet (bool): No output to stdout (True) | Show output (False)

    Returns:
        TYPE: list, AccessKeyIds listed for the IAM user

    """
    metadata, statuscode = query_keyinfo(account, profile, surrogate, quiet)

    if not str(statuscode).startswith('20'):
        fx = inspect.stack()[0][3]
        raise OSError(
                '{}: Problem retrieving access keys for user profile: {}'.format(fx, profile)
            )

    # collect key metadata
    access_keys = [x['AccessKeyId'] for x in metadata]
    key_ct = len(access_keys)    # number keys assoc w/ iam user

    # display access keys for user
    account_stats = [
        ('AWS Account Id: %s' % account),
        ('IAM user id: %s' % (surrogate if surrogate else iam_user)),
        ('profile_name from local awscli config: %s' % profile)
    ]

    if not quiet:
        _display_keylist_header(account, profile, iam_user, surrogate, stage)

    # log record
    [_logging(x) for x in account_stats][0]

    _display_keylist_detail(account, metadata, key_ct, iam_user, surrogate, quiet)
    return access_keys, metadata
