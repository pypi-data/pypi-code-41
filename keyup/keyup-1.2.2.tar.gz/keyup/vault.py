"""
Summary.

    Container module holding reusable objects

"""

import datetime
import pytz
from keyup.common import convert_dt_time
from keyup.statics import local_config
from keyup.variables import act, bd, gn, yl, rd, bdwt, rst
from keyup import logger


global KEYAGE_MIN
KEYAGE_MIN = datetime.timedelta(days=local_config['KEY_METADATA']['KEYAGE_MIN_DAYS'])

global KEYAGE_MAX
KEYAGE_MAX = datetime.timedelta(days=local_config['KEY_METADATA']['KEYAGE_MAX_DAYS'])


def _stage(position):
    return (
            '\n\t'.expandtabs(4) + '________________________________\n\n' +
            ('\t').expandtabs(12) + bd + position +
            '\n\t'.expandtabs(4) + '________________________________'
        )


def _access_keylist(stage):
    accent = yl if 'BEFORE' in stage else gn
    return (
            bdwt + '\n\tAccess Key List'.expandtabs(12) +
            accent + stage +
            '\n' + rst
        )


def _display_keylist_header(acctnum, profilename, user, alias, stage=''):
    # print account metadata to stdout -- header
    if stage:   # active rotation
        title = _access_keylist(_stage(stage))
    else:
        # list operation only, no rotation
        title = (bdwt + '\n\t    Access Key List\n' + rst)
    # print body
    print(
        title + '\n  AWS Account:\t\t' + acctnum +
        '\n  ------------------------------------------'
        )
    print('  IAM User: \t\t%s' % (alias if alias else user))
    print('  Profile Name: \t%s\n' % profilename)


def _display_keylist_detail(awsacct, data, num_keys, user, alias=None, silent=False):
    """
    Summary.

        Print detailed key expiration info to stdout
        Log only if execution in --quiet mode

    Args:
        :data (dict): AWS Access key metadata
        :alias (str): a role used to affect key operations
            instead of an iam_user

    Returns:
        Success || Failure, TYPE: Bool
    """
    # iterate thru keys, output to log + stdout
    for ct, key in enumerate(data):
        age, age_td = _key_age(key['CreateDate'])

        age = (rd + age + rst) if age_td > KEYAGE_MAX else age

        # log metadata
        messages = [
            'AccessKeyId ({}) found for user {}. '.format(
                key['AccessKeyId'], (alias if alias else user)
            ),
            'Key CreateDate: {}. Key Age: {}'.format(
                key['CreateDate'].strftime("%Y-%m-%dT%H:%M:%SZ"), age
            ),
            'Quiet mode, suppress stdout access key list info'
            if silent else 'Access Key info for account {}'.format(awsacct)
        ]
        _logging(messages)

        # print all key metadata to stdout
        if num_keys > 1:
            ct = ct + 1
            keyinfo_header = bd + act + '  AccessKeyId ' + str(ct) + ': '
        else:
            keyinfo_header = bd + act + '  AccessKeyId: \t'

        print(
              keyinfo_header +
              '\t' + act + key['AccessKeyId'] + rst + bd +
              '\n  CreateDate:  ' + rst + '\t\t' +
              key['CreateDate'].strftime("%Y-%m-%d %H:%M UTC") + bd +
              '\n  Age: \t\t\t' + rst + age +
              '\n  Status: ' + rst + '\t\t' + key['Status'] + '\n'
        )


def _logging_map(level, message):
    return {
            "info": logger.info,
            "warn": logger.warning,
            "warning": logger.warning,
            "critical": logger.critical
        }.get(level, logger.info)(message)


def _logging(msg, severity='info'):
    if isinstance(msg, list) or isinstance(msg, tuple):
        for x in msg:
            _logging_map(severity, x)
        return True
    _logging_map(severity, msg)


def _key_age(create_dt):
    """

        Calculates Access key age from today given it's creation date

    Args:
        :**create_dt (datetime object)**: the STS CreateDate parameter returned
          with key key_metadata when an iam access key is created

    Returns:
        TYPE: str, age from today in human readable string format

    """
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    delta_td = now - create_dt
    readable_age = convert_dt_time(delta_td)
    return readable_age, delta_td
