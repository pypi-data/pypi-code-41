# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

from typing import List
import os
import fnmatch
from operator import itemgetter


# Returns config file as a list of strings (one string per line)
def read_config(path: str) -> List[str]:
    config = []
    if os.path.exists(path):
        with open(path, mode="r") as config_file:
            for line in config_file.read().splitlines():
                if len(line) == 0:
                    continue
                config.append(line)
    return config


# Replaces config file with the given
def write_config(path, new_config):
    # Save config categories in reverse alphabetical order
    with open(path, mode="w") as config:
        for line in new_config:
            print(line, file=config)


def add_config(config, key, entry, index=-1):
    # Remove old entry
    remove_config(config, key)

    if index == -1:
        config.append(entry)
    else:
        config.insert(index, entry)


def check_config(config, key):
    """
    Checks if config contains a line matching the parameters.
    Supports globbing in the prefix and name
    """
    for line in config:
        if fnmatch.fnmatch(line, key):
            return config.index(key)
    return -1


def check_config_subdirs(config, prefix, name):
    index = check_config(config, prefix, name)
    if index == -1:
        return check_config(config, prefix, "{}/*".format(name))
    return index


def find_config(config, key):
    """
    Returns index-value pairs for lines in config that match the given key
    """
    lines = []
    for (index, line) in enumerate(config):
        if fnmatch.fnmatch(line, key):
            lines.append((index, line))
    return lines


def find_config_subdirs(config, prefix, name):
    return find_config(config, prefix, name) + find_config(
        config, prefix, "{}/*".format(name)
    )


def Diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif


def remove_config(config, key):
    """
    Removes lines from the config matching the parameters.
    Supports globbing in the prefix and name
    """
    to_remove = find_config(config, key)
    # delete in reverse order to preserve indexes
    for (index, line) in sorted(to_remove, key=itemgetter(0), reverse=True):
        del config[index]
    return to_remove


def remove_config_subdirs(config, prefix, name):
    return remove_config(config, prefix, name) + remove_config(
        config, prefix, "{}/*".format(name)
    )
