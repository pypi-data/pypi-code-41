# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Module for interacting with game configuration files as defined by
Config objects in the profile
"""

from typing import AbstractSet, Any, cast, Dict, Mapping, Optional, Set

import os
import re
import fnmatch
import configparser
from collections import defaultdict
from .atom import Atom, atom_sat
from .deps import get_all_deps
from .usestr import check_required_use, use_reduce
from .loader import load_all_installed
from ..tsort import tsort
from ..masters import get_masters
from ..log import warn
from ..config import get_config, Config
from ..configfile import (
    read_config,
    write_config,
    find_config,
    add_config,
    remove_config,
)
from ..pybuild_interface import InstalledPybuild


def get_config_entries(config: Config, mod: InstalledPybuild):
    """
    Returns a config dictionary or list (depending on config type)
    containing config entries related to the given mod
    """
    if config.ini:
        entries: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))
    else:
        entries: Set[str] = set()

    if config.typ == "INSTALL":
        for install in mod.INSTALL_DIRS:
            if check_required_use(
                install.REQUIRED_USE, mod.INSTALLED_USE, mod.valid_use
            ):
                ipath = '"' + mod.get_dir_path(install).rstrip("/.") + '"'
                if config.ini:
                    section = config_section_pattern(config, INSTALL=ipath, i="*")
                    key = config_key_pattern(config, INSTALL=ipath, i="*")
                    value = config_value_pattern(config, INSTALL=ipath, i="*")
                    entries[section][key] = value
                else:
                    entries.add(config_entry_pattern(config, INSTALL=ipath))
    elif config.typ == "FILE":
        assert config.aux
        for install in mod.INSTALL_DIRS:
            if check_required_use(
                install.REQUIRED_USE, mod.INSTALLED_USE, mod.valid_use
            ):
                for file in install.__dict__.get(config.aux, []):
                    if check_required_use(
                        file.REQUIRED_USE, mod.INSTALLED_USE, mod.valid_use
                    ):
                        if config.ini:
                            section = config_section_pattern(
                                config, **{config.aux: file.NAME, "i": "*"}
                            )
                            key = config_key_pattern(
                                config, **{config.aux: file.NAME, "i": "*"}
                            )
                            value = config_value_pattern(
                                config, **{config.aux: file.NAME, "i": "*"}
                            )
                            entries[section][key] = value
                        else:
                            entries.add(
                                config_entry_pattern(config, **{config.aux: file.NAME})
                            )

    elif config.typ == "FIELD":
        assert config.aux
        dictionary = mod.get_installed_env().get(config.aux)
        if dictionary:
            if config.ini:
                entries.update(dictionary)
            else:
                for section in dictionary:
                    for key in dictionary[section]:
                        entries.add(
                            config_entry_pattern(
                                config,
                                **{
                                    config.aux + "_SECTION": section,
                                    config.aux + "_KEY": key,
                                    config.aux + "_VALUE": dictionary[section][key],
                                },
                            )
                        )
    return entries


def fnmatch_dict(dictionary: Mapping[str, Any], pattern: str) -> Optional[str]:
    """
    Returns a key that matches the given fnmatch-style pattern.
    Matches in a case insensitive value
    """
    for key in dictionary:
        if fnmatch.fnmatch(key.lower(), pattern.lower()):
            return key
    return None


def remove_mod_config(mod: InstalledPybuild):
    """
    Removes entries from the config file that correspond to a given mod

    This may remove entries that do not belong to the mod, but will remove
    all entries that do.

    Be sure to run sort
    """
    for configkey in get_config()["CONFIGS"]:
        config = get_config()["CONFIGS"][configkey]

        entries = get_config_entries(config, mod)

        if config.ini:
            ini = configparser.ConfigParser()
            ini.read(config.path)

            for section in entries:
                inisection = fnmatch_dict(ini, section)
                if inisection:
                    for key in entries[section]:
                        inikey = fnmatch_dict(ini[inisection], key)
                        if inikey and fnmatch.fnmatch(
                            ini[inisection][inikey], entries[section][key]
                        ):
                            del ini[inisection][inikey]
            with open(config.path, "w") as configfile:
                ini.write(configfile)
        else:
            configfile = read_config(config.path)
            for entry in entries:
                remove_config(configfile, entry)
            write_config(config.path, configfile)


def config_entry_pattern(config, **kwargs):
    return config_pattern(config, config.entry_pattern, **kwargs)


def config_section_pattern(config, **kwargs):
    return config_pattern(config, config.section, **kwargs)


def config_key_pattern(config, **kwargs):
    return config_pattern(config, config.key, **kwargs)


def config_value_pattern(config, **kwargs):
    return config_pattern(config, config.value, **kwargs)


def config_pattern(config, pattern, **kwargs):
    if config.spaces_to_underscores:

        def wrapper(s: str):
            return s.replace(" ", "_")

    else:

        def wrapper(s: str):
            return s

    if "section" not in kwargs:
        kwargs["section"] = config.section
    if "key" not in kwargs:
        kwargs["key"] = config.key
    if "value" not in kwargs:
        kwargs["value"] = config.value

    _pattern = pattern.format(**kwargs)
    while any("{" + key + "}" in _pattern for key in kwargs):
        for key in kwargs:
            _pattern = _pattern.replace("{" + key + "}", kwargs[key] or "")
    return wrapper(re.sub("{.*?}", "*", _pattern))


def get_extraneous(config: Config, new, old: Dict[str, Dict[str, str]]):
    if config.ini:
        assert isinstance(new, dict)
        new_dict = cast(Dict[str, Dict[str, AbstractSet[str]]], new)
        results: Dict[str, Dict[str, str]] = defaultdict(dict)
        for section in old:
            for key in old[section]:
                if section in new_dict and key in new_dict[section]:
                    if old[section][key] not in new_dict[section][key]:
                        results[section][key] = old[section][key]

        return results
    else:
        assert isinstance(new, set)
        new_list = cast(AbstractSet[str], new)
        return [
            elem
            for elem in list(filter(lambda x: x not in new_list, old))
            if fnmatch.fnmatch(elem, config_entry_pattern(config))
        ]


def commit_changes(config, new, desc, all_entries=None):
    if config.ini:
        ini = configparser.ConfigParser()
        ini.read(config.path)

        inisection = config_section_pattern(config)
        newentries = {}
        for index, entry in enumerate(new):
            inikey = config_key_pattern(
                config, **{config.aux or config.typ: entry, "i": index}
            )
            inivalue = config_value_pattern(
                config, **{config.aux or config.typ: entry, "i": index}
            )
            newentries[inikey] = inivalue
        old_entries = dict(ini)
    else:
        newentries = {
            config_entry_pattern(config, **{config.aux or config.typ: value})
            for value in new
        }

        config_file = read_config(config.path)
        old_entries = [
            entry
            for (_, entry) in find_config(
                config_file,
                config_entry_pattern(
                    config, **{config.aux or config.typ: "*", "value": "*"}
                ),
            )
        ]

    if all_entries is None:
        all_entries = newentries

    extraneous = get_extraneous(config, all_entries, old_entries)

    if extraneous:
        print()
        print("\n".join(extraneous))
        warn(
            f"The above {desc} were in {config.path} but were not "
            "installed by portmod. They have been appended to the end of the "
            "data directory list."
        )

    if config.ini:
        ini[inisection] = newentries
        for index, value in enumerate(extraneous):
            exkey = config_key_pattern(
                config, **{config.aux: value, "i": index + len(newentries)}
            )
            ini[inisection][exkey] = value

        with open(config.path, "w") as configfile:
            ini.write(configfile)

    else:
        for entry in new:
            add_config(
                config_file,
                config_entry_pattern(
                    config, **{config.aux or config.typ: entry, "value": "*"}
                ),
                config_entry_pattern(config, **{config.aux or config.typ: entry}),
            )
        for entry in extraneous:
            add_config(config_file, entry, entry)

        write_config(config.path, config_file)


def sort_config():
    """Regenerates managed sections of config files"""

    def section_pattern(config, **kwargs):
        if "section" not in kwargs:
            kwargs["section"] = config.section
        if "key" not in kwargs:
            kwargs["key"] = config.key
        if "value" not in kwargs:
            kwargs["value"] = config.value

        pattern = config.section_pattern.format(**kwargs)
        while any("{" + key + "}" in pattern for key in kwargs):
            for key in kwargs:
                pattern = pattern.replace("{" + key + "}", kwargs[key] or "")
        return re.sub("{.*?}", "*", pattern)

    installed = [mod for group in load_all_installed().values() for mod in group]
    for configkey in get_config()["CONFIGS"]:
        config = get_config()["CONFIGS"][configkey]
        print(f"Sorting {config.path} {configkey} entries...")

        if config.typ == "INSTALL":
            # Sort 'data' entries in config
            graph = {}
            priorities = {}
            if config.ini:
                all_entries = defaultdict(lambda: defaultdict(set))
            else:
                all_entries = set()

            # Determine all Directories that are enabled
            for mod in installed:
                for install in mod.INSTALL_DIRS:
                    if check_required_use(
                        install.REQUIRED_USE, mod.INSTALLED_USE, mod.valid_use
                    ):
                        default = os.path.normpath(install.PATCHDIR) == "."
                        path = '"' + mod.get_dir_path(install).rstrip("/.") + '"'
                        graph[(mod.CM, path, default)] = set()
                        priorities[(mod.CM, path, default)] = mod.TIER

            # Add edges in the graph for each data override
            for mod in installed:
                for install in mod.INSTALL_DIRS:
                    if check_required_use(
                        install.REQUIRED_USE, mod.INSTALLED_USE, mod.valid_use
                    ):
                        idefault = os.path.normpath(install.PATCHDIR) == "."
                        ipath = '"' + mod.get_dir_path(install).rstrip("/.") + '"'
                        for parent in get_all_deps(
                            mod.DATA_OVERRIDES + " " + install.DATA_OVERRIDES
                        ):
                            for (atom, path, default) in graph:
                                if atom_sat(Atom(atom), parent) and default:
                                    graph[(atom, path, default)].add(
                                        (mod.CM, ipath, idefault)
                                    )
                                    if config.ini:
                                        section = config_section_pattern(
                                            config, INSTALL=ipath
                                        )
                                        key = config_key_pattern(config, INSTALL=ipath)
                                        value = config_value_pattern(
                                            config, INSTALL=ipath
                                        )
                                        all_entries[section][key].add(value)
                                    else:
                                        all_entries.add(
                                            config_entry_pattern(config, INSTALL=ipath)
                                        )

            sorted_mods = tsort(graph, priorities)

            new_dirs = [path for _, path, _ in sorted_mods]

            commit_changes(config, new_dirs, "Data Directories")
        elif config.typ == "FILE":
            # Sort 'content' entries in config
            # Create graph of content files that are installed, with masters of a file
            # being the parent of the node in the graph
            # Any other content files found in the config should be warned about and
            # removed.
            graph = {}
            priorities = {}

            # Determine all Files that are enabled
            for mod in installed:
                for install in mod.INSTALL_DIRS:
                    if check_required_use(
                        install.REQUIRED_USE, mod.INSTALLED_USE, mod.valid_use
                    ):
                        for file in install.__dict__.get(config.aux, []):
                            if check_required_use(
                                file.REQUIRED_USE, mod.INSTALLED_USE, mod.valid_use
                            ):
                                graph[file.NAME] = set()
                                priorities[file.NAME] = mod.TIER

            for mod in installed:
                for install in mod.INSTALL_DIRS:
                    if check_required_use(
                        install.REQUIRED_USE, mod.INSTALLED_USE, mod.valid_use
                    ):
                        for file in install.__dict__.get(config.aux, []):
                            if check_required_use(
                                file.REQUIRED_USE, mod.INSTALLED_USE, mod.valid_use
                            ):
                                # We need a path to determine masters
                                path = mod.get_file_path(install, file)
                                masters = get_masters(path)
                                masters |= set(
                                    use_reduce(file.OVERRIDES, mod.INSTALLED_USE)
                                )

                                # Add edge from master to child
                                for master in masters:
                                    if graph.get(master) is None:
                                        raise Exception(
                                            "Missing master {} for File {}".format(
                                                master, file.NAME
                                            )
                                        )
                                    graph[master].add(file.NAME)

            new_files = tsort(graph, priorities)

            commit_changes(config, new_files, desc="Files")
        elif config.typ == "FIELD":
            graph = {}
            priorities = {}
            if config.ini:
                all_entries = defaultdict(lambda: defaultdict(set))
            else:
                all_entries = set()

            for mod in installed:
                graph[(mod.CM, mod)] = set()
                priorities[(mod.CM, mod)] = mod.TIER
                for parent in get_all_deps(mod.DATA_OVERRIDES):
                    for (atom, values) in graph:
                        if atom_sat(Atom(atom), parent):
                            graph[(atom, values)].add((mod.CM, mod))

            sections = defaultdict(dict)
            for _, mod in tsort(graph, priorities):
                dictionary = mod.get_installed_env().get(config.aux)
                if dictionary:
                    for section in dictionary:
                        sections[section].update(dictionary[section])

                        for key in dictionary[section]:
                            if config.ini:
                                all_entries[section][key].add(dictionary[section][key])
                            else:
                                all_entries.add(
                                    config_entry_pattern(
                                        config,
                                        **{
                                            config.aux + "_SECTION": section,
                                            config.aux + "_KEY": key,
                                            config.aux
                                            + "_VALUE": dictionary[section][key],
                                        },
                                    )
                                )

            if config.ini:
                ini = configparser.ConfigParser()
                ini.read(config.path)
            else:
                config_file = read_config(config.path)
                old = [
                    entry
                    for _, entry in find_config(
                        config_file,
                        config_entry_pattern(config, **{config.aux: "*", "value": "*"}),
                    )
                ]
                extraneous = get_extraneous(config, all_entries, old)

                if extraneous:
                    print()
                    print("\n".join(extraneous))
                    warn(
                        f"The above config entries were in {config.path} but were not "
                        "added by portmod. They have been appended to the end of the "
                        "list."
                    )

            for section in sections:
                if config.ini:
                    inisection = config_section_pattern(
                        config, **{config.aux + "_SECTION": section}
                    )
                    for index, key in enumerate(sections[section]):
                        inikey = config_key_pattern(
                            config, **{config.aux + "_KEY": key, "i": index}
                        )
                        inivalue = config_value_pattern(
                            config,
                            **{
                                config.aux + "_VALUE": sections[section][key],
                                "i": index,
                            },
                        )
                        if inisection not in ini:
                            ini[inisection] = {}
                        ini[inisection][inikey] = inivalue
                else:
                    for key in sections[section]:
                        add_config(
                            config_file,
                            config_entry_pattern(
                                config,
                                **{
                                    config.aux + "_SECTION": section,
                                    config.aux + "_KEY": key,
                                    "value": "*",
                                },
                            ),
                            config_entry_pattern(
                                config,
                                **{
                                    config.aux + "_SECTION": section,
                                    config.aux + "_KEY": key,
                                    config.aux + "_VALUE": sections[section][key],
                                },
                            ),
                        )

            if config.ini:
                with open(config.path, "w") as configfile:
                    ini.write(configfile)
            else:
                for entry in extraneous:
                    add_config(config_file, entry, entry)

                write_config(config.path, config_file)

        elif config.typ == "STATIC":
            if config.ini:
                ini = configparser.ConfigParser()
                ini.read(config.path)

                key = config_key_pattern(config)
                value = config_value_pattern(config)
                ini[key] = value

                with open(config.path, "w") as configfile:
                    ini.write(configfile)
            else:
                config_file = read_config(config.path)

                add_config(
                    config_file,
                    config_entry_pattern(config, **{"value": "*"}),
                    config_entry_pattern(config),
                )

                write_config(config.path, config_file)
        else:
            warn(f"Skipping unsupported config type {config.typ}")
            continue
