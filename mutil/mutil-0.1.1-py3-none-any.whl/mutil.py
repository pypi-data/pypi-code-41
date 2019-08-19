#!/usr/bin/env python3
#===============================================================================
# mutil.py
#===============================================================================

"""Utilities for managing the memory policy"""




# Imports ======================================================================

import json
# import math
import os
# import psutil
import socket
import sys
import subprocess

hostname = socket.gethostname()
if hostname == 'gatsby.ucsd.edu':
    sys.path.append('/home/data/kglab-python3-modules')
elif hostname == 'holden':
    sys.path.append('/lab/kglab-python3-modules')

from fancyprint import fprint




# Globals ======================================================================

if hostname == 'gatsby.ucsd.edu':
    PROPOSED_POLICY_PATH = (
        '/home/data/memory_policy/proposed_memory_policy.json'
    )
    CURRENT_POLICY_PATH = '/home/data/memory_policy/current_memory_policy.json'
    PREVIOUS_POLICY_PATH= '/home/data/memory_policy/previous_memory_policy.json'
elif (hostname == 'holden') or (hostname == 'anthony-MacBookPro'):
    PROPOSED_POLICY_PATH = '/lab/memory_policy/proposed_memory_policy.json'
    CURRENT_POLICY_PATH = '/lab/memory_policy/current_memory_policy.json'
    PREVIOUS_POLICY_PATH= '/lab/memory_policy/previous_memory_policy.json'

CGCONFIG_BASE = ''
CGCONFIG_PATH = '/etc/cgconfig.conf'
CGRULES_PATH = '/etc/cgrules.conf'
CGRULES_BASE  = '\t'.join(('#<user/group>', '<controller(s)>', '<cgroup>'))
MEMORY_CUSHION_GB = 8




# Functions ====================================================================

def require_super_user():
    """Check that the current command is being run with superuser privileges
    
    Raise an exception if it is not.
    """
    
    if not os.geteuid() == 0:
        raise SystemExit('Superuser required')


def load_policy(policy_path):
    """Load a memory policy (JSON file) from disk
    
    Parameters
    ----------
    policy_path : str
        Path to the memory policy file
    
    Returns
    -------
    dict
        Dictionary defining a memory policy
    """
    
    with open(policy_path, 'r') as f:
        policy = json.load(f)
    return policy


def get_usage_for_a_user(user):
    """Get estimated memory usage for a user
    
    Parameters
    ----------
    user : str
        User to retrieve
    
    Returns
    -------
    int
        Estimated memory usage in bytes
    """

    with subprocess.Popen(
        ('ps', '-U', user, '--no-headers', '-o', 'rss'),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    ) as ps:
        with subprocess.Popen(
            ('awk', '{ sum+=$1} END {print sum}'),
            stdin=ps.stdout,
            stdout=subprocess.PIPE
        ) as awk:
            usage_bytes, _ = awk.communicate()
            usage_str = usage_bytes.decode().rstrip('\n')
            return int(usage_str) if usage_str else 0


def convert_usage(usage, kilobytes=False, megabytes=False):
    """Convert units of memory

    Converts to gigabytes unless the `kilobytes` or `megabytes` argument is
    given.
    
    Parameters
    ----------
    usage : int
        Memory usage in bytes
    kilobytes : bool
        Convert to kilobytes
    megabytes : bool
        Convert to megabytes
    
    Returns
    -------
    int
        Converted value
    """

    return int(usage / (1024 ** (2 - (2 * kilobytes) - (1 * megabytes))))


def check_dark_background_config():
    return os.path.isfile(
        os.path.join(
            os.path.expanduser('~'),
            '.mdark'
        )
    )


def determine_color(memory_limit_gb, memory_usage_gb, dark_background=False):
    """Determine a display color based on percent memory usage
    
    Parameters
    ----------
    memory_limit_gb : int
        Overall memory limit in gigabytes
    memory_usage_gb : int
        Memory usage value in gigabytes
    dark_background : bool
        Use a dark background color schme
    
    Returns
    -------
    str
        Color string for `fancyprint.fprint`
    """

    for threshold, color in zip(
        (memory_limit_gb * x / 4 for x in (3, 2, 1, 0)),
        (
            ('r', 'y', 'g', 'c')
            if dark_background else ('dr', 'dy', 'dg', 'dc')
        )
    ):
        if memory_usage_gb > threshold:
            return color
    else:
        return ''


def fancy_print_shared(
    memory_limit_gb,
    shared_memory,
    dark_background=False,
    comma=False
):
    """Fancy print the shared memory value
    
    Parameters
    ----------
    memory_limit_gb : int
        Overall memory limit in gigabytes
    shared_memory : int
        Shared memory usage in gigabytes
    """

    fprint(
        '  "shared": {}{}'.format(shared_memory, ',' * comma),
        color=determine_color(
            memory_limit_gb,
            shared_memory,
            dark_background=dark_background
        )
    )


def fancy_print_group(
    memory_limit_gb,
    group_name,
    group,
    dark_background=False,
    comma=False
):
    """Fancy print the shared memory value
    
    Parameters
    ----------
    memory_limit_gb : int
        Overall memory limit in gigabytes
    shared_memory : int
        Shared memory usage in gigabytes
    """

    group_usage = convert_usage(
        sum(get_usage_for_a_user(user) for user in group['users'])
    )
    fprint(
        '  "{}"'.format(group_name),
        color=determine_color(
            memory_limit_gb,
            group_usage,
            dark_background=dark_background
        ),
        end=''
    )
    print(': {')
    lines = json.dumps(group, indent=2, sort_keys=True).splitlines()[1:]
    for line in lines:
        if line.strip(' :",') in group['users']:
            color = determine_color(
                memory_limit_gb,
                convert_usage(get_usage_for_a_user(line.strip(' :",'))),
                dark_background=dark_background
            )
            fprint('  {}'.format(line.rstrip(',')), color=color, end='')
            print(',')
        else:
            print('  {}{}'.format(line, ',' * (line == '}' and comma)))
    


def print_policy(policy, fancy=False, dark_background=False):
    """Print a memory policy (JSON file) to standard output
    
    Parameters
    ----------
    policy : dict
        Dictionary defining the policy
    """

    if not fancy:
        print(json.dumps(policy, indent=2, sort_keys=True))
        return
    
    memory_limit_gb = memory_limit_in_gigabytes()
    sorted_keys = sorted(policy.keys())

    print('{')
    for key in sorted_keys:
        if key == 'shared':
            fancy_print_shared(
                memory_limit_gb,
                policy['shared'],
                dark_background=dark_background,
                comma=key != sorted_keys[-1]
            )
            continue
        fancy_print_group(
            memory_limit_gb,
            key,
            policy[key],
            dark_background=dark_background,
            comma=key != sorted_keys[-1]
        )
    print('}')


def dump_policy(policy, policy_path):
    """Write a memory policy (JSON file) to disk
    
    Parameters
    ----------
    policy : dict
        Dictionary defining the policy
    policy_path : str
        Path to write the memory policy file
    """
    
    with open(policy_path, 'w') as f:
        json.dump(policy, f)


def get_group_set(policy):
    """Get the set of group names in a policy
    
    Parameters
    ----------
    policy : dict
        Dictionary defining the policy
    
    Returns
    -------
    set
        The group names in the policy
    """
    
    return set(policy.keys()) - {'shared'}


def get_user_set(policy):
    """Get the set of users in a policy
    
    Parameters
    ----------
    policy : dict
        Dictionary defining the policy
    
    Returns
    -------
    set
        The users in the policy
    """
    
    return set(
        user
        for group in get_group_set(policy)
        for user in policy[group]['users']
)


def validate_user(user, users):
    """Check if a user is contained in the indicated group of users
    
    Raise an exception if not.
    
    Parameters
    ----------
    user : str
        User to validate
    users : container
        Container of valid users
    """
    if user not in users:
        raise Exception(
            "It looks like you're trying to free memory before being inducted "
            'into the policy. Use "minduct" to induct yourself before'
            ' continuing.'
        )


def validate_group(group_name):
    """Check that a group of users is not named ``free`` or ``shared``
    
    Parameters
    ----------
    group_name : str
        Group name to be validated
    """
    
    if group_name == 'free':
        raise Exception(
            'Can\'t free memory from the "free" group... it\'s already free.'
        )
    elif group_name == 'shared':
        raise Exception('"shared" can\'t be a group name')


def specified_users(users_arg, users):
    """Parse a comma-separated list of users
    
    Check that all specified users are valid, and return them as a list
    
    Parameters
    ----------
    users_arg : str
        Comma-separated list of users
    users : container
        Container of valid users
    
    Returns
    -------
    list
        List of specified users
    """
    if set(users_arg.split(',')) <= users:
        users = users_arg.split(',')
        return users
    else:
        raise Exception(
            'Some of the specified users have not yet been inducted into the '
            'policy. Use minduct -u to induct them before continuing.'
        )


def remove_user_from_current_group(user, policy):
    """Remove a user from a group they are currently a member of
    
    Parameters
    ----------
    user : str
        User to remove
    policy : dict
        Policy to modify
    """
    
    for group in get_group_set(policy):
        if user in policy[group]['users']:
            if (policy[group]['users'] == [user]) and (group != 'free'):
                del policy[group]
            else:
                policy[group]['users'].remove(user)
            break


def free_gigabytes():
    """Wraps the unix command `free -g`
    
    Returns
    -------
    tuple
        total, used, free, shared, buff_cache, available
    """
    
    with subprocess.Popen(('free', '-g'), stdout=subprocess.PIPE) as proc:
        return (
            int(val) for val in
            proc.communicate()[0].decode().splitlines()[1].split()[1:]
        )


def memory_limit_in_gigabytes():
    """Calculate the memory limit in gigabytes
    
    Returns
    -------
    int
        The memory limit (in gigabytes)
    """
    
    _, used, _, _, _, available = free_gigabytes()
    return used + available - MEMORY_CUSHION_GB
#     return math.floor(
#         (psutil.virtual_memory().available + psutil.virtual_memory().used)
#         / 2**30
#     )


def shared_memory_in_gigabytes():
    """Look up the shared memory in gigabytes
    
    Returns
    -------
    int
        The shared memory (in gigabytes)
    """
    
    _, _, _, shared, _, _ = free_gigabytes()
    return shared
#     return math.floor(psutil.virtual_memory().shared / 2**30)


def available_memory(policy):
    """Calculate the available memory in gigabytes
    
    Returns
    -------
    int
        The available memory (in gigabytes)
    """
    
    limit = memory_limit_in_gigabytes()
    available_memory_in_gigabytes = (
        limit - sum(
            policy[group]['memory_limit']
            for group in get_group_set(policy) - {'free'}
        )
    )
    if available_memory_in_gigabytes < 16:
        raise Exception(
            'This action would bring the total reserved memory above {} GB, '
            'which is not allowed. Please reserve less.'
            .format(limit - 16)
        )
    else:
        return available_memory_in_gigabytes


def reserved_memory(policy):
    """Calculate the amount of reserved memory according to the given policy
    
    Returns
    -------
    int
        The reserved memory (in gigabytes)
    """
    return sum(
        policy[group]['memory_limit']
        for policy in get_group_set(policy) - {'free'}
    )


def validate_draft_policy(
    draft,
    total_reserved_memory,
    draft_users,
    proposed_policy_users
):
    """Check that a draft policy is valid, and raise an exception if not
    
    Parameters
    ----------
    draft : dict
        Dictionary defining the draft policy
    total_reserved_memory : int
        The total memory reserved by the draft policy in gigabytes
    draft_users : set
        The users present in the draft
    proposed_policy_users : set
        The users present in the extant proposed policy
    """
    
    if {'free', 'shared'} < set(draft.keys()):
        raise Exception(
            '"free" and "shared" are reserved words and should not be group '
            'names in a policy draft.'
        )
    limit = memory_limit_in_gigabytes()
    if total_reserved_memory >= (limit - 16):
        raise Exception(
            'This draft reserves more than {} GB of memory, please reserve '
            'less.'
            .format(limit - 16)
        )
    for user in draft_users:
        if user not in proposed_policy_users:
            raise Exception(
                'Induct new users before drafting a policy that includes them'
            )


def infer_free_group(
    draft,
    total_reserved_memory,
    draft_users,
    proposed_policy_users
):
    """Infer the free group for a draft policy
    
    Parameters
    ----------
    draft : dict
        Dictionary defining the draft policy
    total_reserved_memory : int
        The total memory reserved by the draft policy in gigabytes
    draft_users : set
        The users present in the draft
    proposed_policy_users : set
        The users present in the extant proposed policy
    
    Returns
    -------
    dict
        The "free" group to fill out a memory policy
    """
    
    return {
        'memory_limit': memory_limit_in_gigabytes() - total_reserved_memory,
        'users': list(proposed_policy_users - draft_users)
    }


def generate_config_files(policy):
    """Generate config files for cgroups
    
    Parameters
    ----------
    policy : dict
        Dictionary defining a memory policy
    
    Returns
    -------
    str, str
        Tuple of two strings: the cgconfig and cgrules files, respectively.
    """
    
    hostname = socket.gethostname()
    cgconfig_list = [CGCONFIG_BASE]
    cgrules_list = [CGRULES_BASE]
    for group in get_group_set(policy):
        if hostname == 'gatsby.ucsd.edu':
            cgconfig_list.append(
                (
'''group {0} {{
    memory {{
        memory.limit_in_bytes="{1}G";
        memory.memsw.limit_in_bytes="{1}G";
    }}
}}

'''
                ).format(group, policy[group]['memory_limit'])
            )
        elif (hostname == 'holden') or (hostname == 'anthony-MacBookPro'):
            cgconfig_list.append(
                (
'''group {0} {{
    memory {{
        memory.limit_in_bytes="{1}G";
        memory.swappiness=0;
    }}
}}

'''
                ).format(group, policy[group]['memory_limit'])
            )
        for user in policy[group]['users']:
            cgrules_list.append('\t'.join((user, 'memory', group)))
    return ''.join(cgconfig_list), '\n'.join(cgrules_list) + '\n'


def restart_daemons():
    """Restart the cgroups daemons (putting a configuration into effect)"""
    
    hostname = socket.gethostname()
    if hostname == 'gatsby.ucsd.edu':
        subprocess.call(('service', 'cgconfig', 'restart'))
    elif hostname == 'holden':
        subprocess.call(('cgconfigparser', '-l', '/etc/cgconfig.conf'))
    subprocess.call(('service', 'cgred', 'restart'))


def enact_policy(policy, no_daemon=False):
    """Enact a memory policy by writing new cgroup config files
    
    Restart the daemons if required
    
    Parameters
    ----------
    policy : dict
        Memory policy to enact
    no_daemon : bool
        If True, don't restart the cgroup daemons
    """
    
    cgconfig, cgrules = generate_config_files(policy)
    with open(CGCONFIG_PATH, 'w') as f:
        f.write(cgconfig)
    with open(CGRULES_PATH, 'w') as f:
        f.write(cgrules)
    if no_daemon:
        subprocess.call(('cgconfigparser', '-l', '/etc/cgconfig.conf'))
    else:
        restart_daemons()
