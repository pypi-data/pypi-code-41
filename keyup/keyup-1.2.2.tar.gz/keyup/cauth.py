"""
Key Report Generation Module:
    - Centralized authentication module for producing Key Report
    - Uses threading for concurrent processing

Module Functions:
    - convert:
        Converts time units to hours
    - discover_account_affiliations:
        maps awscli profile users to corresponding iam user ids
    - expired_keys:
        determines if an access keyset is aged beyond max age value in
        keyup's configuration file
    - display_table:
        renders vpt table to cli stdout
"""

import os
import sys
import datetime
import inspect
import pytz
import unicodedata
from botocore.exceptions import ClientError

# 3rd party
from veryprettytable import VeryPrettyTable
from pyaws.session import boto3_session
from libtools.js import export_iterobject
from libtools import stdout_message
from libtools import Colors
from keyup.iam_operations import local_profilenames
from keyup.map import map_identity
from keyup.vault import KEYAGE_MAX
from keyup.colormap import ColorMap
from keyup.statics import local_config
from keyup import keyconfig, logger


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


cm = ColorMap()

# universal colors
yl = Colors.YELLOW + Colors.BOLD
fs = Colors.GOLD3
bd = Colors.BOLD
gn = Colors.BRIGHT_GREEN
btext = text + Colors.BOLD
bdwt = cm.bdwt
dgray = cm.dg1
frame = text
ub = Colors.UNBOLD
cmark = unicodedata.lookup('heavy check mark')
xmark = unicodedata.lookup('LIGHT SALTIRE')
rst = Colors.RESET


tablespec = {
    'border': True,
    'header': True,
    'padding': 2,
    'field_max_width': 70
}

column_widths = {
    'ProfileName': 16,
    'iam_user': 14,
    'account': 16,
    'CreateDate': 22,
    'time_remaining': 14
}


class authentication():
    """
        class def for generation and retention of a single set of credentials
        for generating key-report via a single iam user priviledges
    """
    def __init__(self, profile):
        self.profile_name = profile
        self.iam_user = None
        self.access_key = None
        self.secret_key = None

        if (self.access_key or self.secret_key) is None:
            self.generate_token(self.iam_user)

    def generate_token(self, user):
        pass


def convert(dt):
    """Convert days to hours"""
    expiration_date = dt + KEYAGE_MAX
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    if now < expiration_date and (expiration_date - now).days == 0:
        return (expiration_date - now).seconds / 3600


def discover_account_affiliations():
    """
        Associates each profile name in local awscli configuration
        to an iam username and an AWS Account Number

    Returns:
        affiliation info, TYPE: dict

    .. code: json

        {
            profile_name: {
                "account": 104713565656,
                "iam_user": admin-sandbox2
            }
        }

    """
    affiliations = {}

    for profile in local_profilenames():
        try:
            iam_user, aws_account = map_identity(profile)
            affiliations[profile] = {'iam_user': iam_user, 'account': aws_account}
        except ClientError:
            fname = inspect.stack()[0][3]
            logger.info(
                '{}: Unable to locate aws account for profile {}'.format(fname, profile))
            continue
    return affiliations


def display_skipped(iam_users):
    """
    Display iam users exceptions skipped in the key report
    """
    tab1 = '\t'.expandtabs(34)
    tab2 = '\t'.expandtabs(46)
    stdout_message(
            message=f'{cm.gray}Users failing authentication omitted from report:',
            indent=30
        )
    for user in iam_users:
        print('{}-  {}'.format(tab2, user))


def display_table(table, exceptions, tabspaces=4):
    """
    Print Table Object offset from left by tabspaces
    """
    indent = ('\t').expandtabs(tabspaces)
    table_str = table.get_string()
    for e in table_str.split('\n'):
        print(indent + frame + e)
    sys.stdout.write(Colors.RESET + '\n')
    display_skipped(exceptions) if exceptions else print('')
    sys.stdout.write(Colors.RESET + '\n\n')
    return True


def expired_keys(dt):
    """
    Convert datetime objects into human readable
    """
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    delta_td = now - dt
    if delta_td < KEYAGE_MAX:
        return False
    return True


def format_remaining(days: int):
    """
        Formats days remaining value

    Returns:
        days (int) with appropriate color, spacing format applied
    """
    def spacing():
        s = ''
        for digit in str(days):
            s = s + ' '
        return s

    if (0 <= days < KEYAGE_WARNING):
        return cm.yl + spacing() + str(round(days)) + ' days' + rst
    elif days < 0:
        return cm.brd + spacing() + str(round(days / -1)) + 'd overdue' + rst
    else:
        return str(days) + ' days'


def print_header(title, indent=4, spacing=4):
    """
    Paints title header grid of a vpt Table
    """
    divbar = frame + '-'
    upbar = frame + '|' + rst
    ltab = '\t'.expandtabs(indent)              # lhs indentation of title bar
    spac = '\t'.expandtabs(7)                   # rhs indentation of legend from divider bar
    tab4 = '\t'.expandtabs(4)                   # space between legend items
    tab5 = '\t'.expandtabs(5)                   # space between legend items
    tab6 = '\t'.expandtabs(6)                   # space between legend items
    # construct legend
    valid = '{} valid{}'.format(gn + bd + 'o' + rst, tab5)
    near = '{} near expiration{}'.format(yl + bd + 'o' + rst, tab5)
    exp = '{} expired'.format(cm.brd + bd + 'o' + rst)
    # output header
    print('\n\n\n')
    print(tab4, end='')
    print(divbar * 119, end='')
    print('\n' + tab4 + upbar + frame + '\t|'.expandtabs(60) + rst + frame + '\t|'.expandtabs(56) + rst)
    print('{}{}{}{}{}{}'.format(tab4 + upbar + ltab, title + spac, valid, near, exp, tab6 + upbar))
    print(tab4 + upbar + frame + '\t|'.expandtabs(60) + rst + frame + '\t|'.expandtabs(56) + rst)
    return True


def spacing(days):
    s = ''
    for digit in str(days):
        s = s + ' '
    return s


def time_remaining(dt):
    """Calculate the days until expiration"""
    expiration_date = dt + KEYAGE_MAX
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    if now < expiration_date:
        return (expiration_date - now).days
    return -1 * (now - expiration_date).days


def _postprocessing():
    return True


def setup_table(user_data, exception_list):
    """
    Renders Table containing data elements via cli stdout
    """
    # setup table
    x = VeryPrettyTable(
            border=tablespec['border'],
            header=tablespec['header'],
            padding_width=tablespec['padding']
        )

    x.field_names = [
        bdwt + 'ProfileName' + frame,
        bdwt + 'IAM User' + frame,
        bdwt + 'AWS AccountId' + frame,
        bdwt + 'CreateDate' + frame,
        bdwt + 'Time Remaining' + frame,
        bdwt + 'Status' + frame,
    ]

    # cell max width
    x.max_width[bdwt + 'ProfileName' + frame] = column_widths['ProfileName']
    x.max_width[bdwt + 'IAM User' + frame] = column_widths['iam_user']
    x.max_width[bdwt + 'AWS AccountId' + frame] = column_widths['account']
    x.max_width[bdwt + 'CreateDate' + frame] = column_widths['CreateDate']
    x.max_width[bdwt + 'Time Remaining' + frame] = column_widths['time_remaining']

    # cell min = max width
    x.min_width[bdwt + 'ProfileName' + frame] = x.max_width[bdwt + 'ProfileName' + frame]
    x.min_width[bdwt + 'IAM User' + frame] = x.max_width[bdwt + 'IAM User' + frame]
    x.min_width[bdwt + 'AWS AccountId' + frame] = x.max_width[bdwt + 'AWS AccountId' + frame]
    x.min_width[bdwt + 'CreateDate' + frame] = x.max_width[bdwt + 'CreateDate' + frame]
    x.min_width[bdwt + 'Time Remaining' + frame] = column_widths['time_remaining']

    # cell alignment
    x.align[bdwt + 'ProfileName' + frame] = 'l'
    x.align[bdwt + 'IAM User' + frame] = 'l'
    x.align[bdwt + 'AWS AccountId' + frame] = 'l'
    x.align[bdwt + 'CreateDate' + frame] = 'c'
    x.align[bdwt + 'Time Remaining' + frame] = 'c'
    x.align[bdwt + 'Status' + frame] = 'c'

    # populate table
    for k, v in user_data.items():

            dt = v['CreateDate']
            expired = expired_keys(v['CreateDate'])
            _days = time_remaining(dt)
            k = truncate_fields(k)
            v = truncate_fields(v)

            if not expired and (0 <= _days < KEYAGE_WARNING):
                # close to expiration, warning
                profilename = yl + k + rst
                user = yl + v['iam_user'] + rst
                accountId = yl + v['account'] + rst
                createdate = yl + dt.strftime('%b %d, %Y %H:%M UTC') + rst
                remaining = yl + str(_days) + ' days' + rst if _days > 1 else yl + str(_days) + ' day' + rst
                status = yl + cmark + rst

                # < 1 day remains; calculate hours remaining
                if _days == 0:
                    remaining = yl + str(int(round(convert(dt)))) + ' hrs' + spacing(int(round(convert(dt)))) + rst

            else:
                #  key credentials are either expired (age > KEYAGE_MAX) or valid
                profilename = cm.brd + k + rst if expired else k
                user = cm.brd + v['iam_user'] + rst if expired else v['iam_user']
                accountId = cm.brd + v['account'] + rst if expired else v['account']
                createdate = cm.brd + dt.strftime('%b %d, %Y %H:%M UTC') + rst if expired else dt.strftime('%b %d, %Y %H:%M UTC')
                remaining = format_remaining(_days)
                status = (cm.brd + xmark + rst if expired else gn + bd + cmark + rst)

                if _days == 1:
                    remaining = str(_days) + ' day'

            x.add_row(
                [
                    rst + profilename + frame,
                    rst + user + frame,
                    rst + accountId + frame,
                    rst + createdate + frame,
                    rst + remaining + frame,
                    rst + status + frame
                ]
            )

    # Table
    vtab_int = 9
    vtab = '\t'.expandtabs(vtab_int)
    msg = '{}AWS Identity Access Key Expiration Report{}{}|{}'.format(btext, rst + frame, vtab, rst)
    print_header(title=msg, indent=10, spacing=vtab_int)
    display_table(x, exception_list, tabspaces=4)
    return _postprocessing()


def source_globals():
    """
    global environment variable definitions
    """
    global KEYAGE_WARNING
    KEYAGE_WARNING = local_config['KEY_METADATA']['KEYAGE_WARNING']


def truncate_fields(element):
    """
        Truncates table field data to align with max column width

    Returns:
        truncated element, TYPE: dict or str
    """
    if isinstance(element, dict):
        for k, v in element.items():
            for name, width in column_widths.items():
                if k == name and k != 'CreateDate':
                    element[k] = v[:width]
        return element
    return element[:column_widths['ProfileName']]


def prepare_reportdata(debug=False):
    """
        Prints out key expiration info for all profilenames associated with
        the primary profilename given to access the account information

    """
    try:

        source_globals()

    except KeyError:
        # remove offending configuration file, then recreate
        if os.path.exists(local_config['PROJECT']['CONFIG_PATH']):
            os.remove(local_config['PROJECT']['CONFIG_PATH'])
        return keyconfig.option_configure(False, local_config['PROJECT']['CONFIG_PATH'])

    data, aliases = {}, {}
    exceptions = []
    affiliations = discover_account_affiliations()

    if debug:
        export_iterobject(affiliations)

    for k, v in affiliations.items():

        account = v['account']

        try:
            r = None
            client = boto3_session(service='iam', profile=k)
            r = client.list_access_keys()
            key_metadata = r['AccessKeyMetadata']

            if debug:
                stdout_message(
                    message='Key information received for profile {}'.format(bd + k + rst),
                    prefix='OK'
                )

        except ClientError as e:
            fname = inspect.stack()[0][3]
            logger.info('{}: Unable to list key info for profile {}. Error {}'.format(fname, k, e))
            exceptions.append(k)
            continue

        try:

            if aliases.get(account):
                alias = aliases[account]
            else:
                # human readable name of the account
                alias = client.list_account_aliases()['AccountAliases'][0]

                # store identified aliases
                aliases[account] = alias

        except ClientError:
            alias = ''

        accountId = alias or account
        iam_user = key_metadata[0]['UserName']
        status = key_metadata[0]['Status']
        metadata = key_metadata[0]['CreateDate']

        data[k] = {
            'account': accountId,
            'iam_user': iam_user,
            'status': status,
            'CreateDate': metadata
        }

        logger.info('IAM User {} key info found for AWS account {}'.format(iam_user, accountId))
    return data, exceptions
