# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3
"""
Module that interacts with the portmod config file

Files are stored both in the portmod local directory and in the profile directory tree,
with the user's config file overriding and extending defaults set by the profile
"""

from typing import Dict, Optional
import os
import string
import sys
from functools import lru_cache
from RestrictedPython import compile_restricted
from pkg_resources import get_distribution
from .globals import env
from .repo.profiles import profile_parents
from .repo.flags import collapse_flags

__COLLAPSE_KEYS = {
    "USE",
    "ACCEPT_LICENSE",
    "ACCEPT_KEYWORDS",
    "INFO_VARS",
    "USE_EXPAND",
    "USE_EXPAND_HIDDEN",
    "PROFILE_ONLY_VARIABLES",
}
__OVERRIDE_KEYS = {"ARCH", "TEXTURE_SIZE", "PORTMOD_MIRRORS"}


class Config:
    def __init__(
        self,
        path: str,
        typ: str,
        aux: Optional[str] = None,
        section_pattern: Optional[str] = None,
        entry_pattern: Optional[str] = None,
        section: Optional[str] = None,
        key: Optional[str] = None,
        value: Optional[str] = None,
        spaces_to_underscores: bool = False,
        ini: bool = False,
    ):
        self.path = os.path.expanduser(path)
        self.typ = typ
        self.aux = aux
        self.section_pattern = section_pattern
        self.entry_pattern = entry_pattern
        self.section = section
        self.key = key
        self.value = value
        self.spaces_to_underscores = spaces_to_underscores
        self.ini = ini

    def __repr__(self):
        return f"Config({self.path}, type={self.typ}, aux={self.aux})"


def create_config_placeholder():
    """
    Creates a placeholder config file to help the user initialize their
    config file for the first time
    """
    os.makedirs(env.PORTMOD_CONFIG_DIR, exist_ok=True)
    version = get_distribution("portmod").version
    with open(env.PORTMOD_CONFIG, "w") as file:
        config_string = f"""# This is a placeholder config file for Portmod {version}
# This file is created if no config file is found, and not updated when Portmod updates.
# To regenerate this config file for the latest version of Portmod, delete it and run
#    `omwmerge --info`

# This file contains optional config values that override those set by your profile
# See https://gitlab.com/portmod/portmod/wikis/Portmod-Config for a full description
# of the options used by Portmod itself.
# Note that some variables may be used for specific Pybuilds and may not be listed
# on the wiki

# Valid global use flags can be found in the profiles/use.yaml file of the repository
# Default USE flag configurations vary with the profile
# USE=""

# Valid TEXTURE_SIZE options are
# max
# min
# max <= SIZE (e.g. 2048)
# min >= SIZE
#
# The default is "min"
# TEXTURE_SIZE="min"

# Keywords to accept. Valid choices at the global level are arch (stable mods only) and
# ~arch (stable and testing mods). Defaults to arch
# ACCEPT_KEYWORDS="openmw"

# Licenses to accept. This will prevent installation of mods using those licenses unless
# overridden by a mod-specific rule in mods.accept_license
# Defaults to "* -EULA"
# ACCEPT_LICENSE="* -EULA"

# Auto-detected by default, however if it fails to detect the location, specify it here
# OPENMW_CONFIG="/path/to/config"

# Auto-detected by default, however if it fails to detect the location, specify it here
# Note that this should be the root where the executable is found,
# not the data files directory
# MORROWIND_PATH="/path/to/Morrowind"
"""
        print(config_string, file=file)


def read_config(path: str, old_config: Dict, *, user: bool = False) -> Dict:
    """
    Reads a config file and converts the relevant fields into a dictionary
    """
    with open(path, "r") as file:
        config = file.read()

    byte_code = compile_restricted(config, filename=path, mode="exec")
    glob = {"__builtins__": {"join": os.path.join, "Config": Config}}
    new_config = old_config.copy()
    try:
        exec(byte_code, glob, new_config)
    except NameError as e:
        print(e, "in", path)
    except SyntaxError as e:
        print(e, "in", path)

    merged = old_config.copy()

    def line_of_key(key: str) -> Optional[int]:
        for index, line in enumerate(config.split("\n")):
            if key in line:
                return index
        return None

    for key in __COLLAPSE_KEYS:
        if (
            user
            and key in merged.get("PROFILE_ONLY_VARIABLES", [])
            and new_config.get(key) is not None
            and new_config.get(key) != old_config.get(key)
        ):
            raise UserWarning(
                f"{path}:{line_of_key(key)}\n"
                f"Variable {key} is reserved for use in profiles "
                "and cannot be overridden or modified"
            )

        if isinstance(new_config.get(key, ""), str):
            new_config[key] = set(new_config.get(key, "").split())
        merged[key] = collapse_flags(merged.get(key, set()), new_config.get(key, set()))

    for key in __OVERRIDE_KEYS:
        if (
            user
            and key in merged.get("PROFILE_ONLY_VARIABLES", [])
            and new_config.get(key) is not None
            and new_config.get(key) != old_config.get(key)
        ):
            raise UserWarning(
                f"{path}:{line_of_key(key)}\n"
                f"Variable {key} is reserved for use in profiles "
                "and cannot be overridden or modified"
            )

        if key in new_config and new_config[key]:
            merged[key] = new_config.get(key)

    for key in old_config.keys() | new_config.keys():
        if (
            user
            and key in merged.get("PROFILE_ONLY_VARIABLES", [])
            and new_config.get(key) is not None
            and new_config.get(key) != old_config.get(key)
        ):
            raise UserWarning(
                f"{path}:{line_of_key(key)}\n"
                f"Variable {key} is reserved for use in profiles "
                "and cannot be overridden or modified"
            )

        if key not in __COLLAPSE_KEYS | __OVERRIDE_KEYS:
            if key in new_config:
                merged[key] = new_config[key]
            else:
                merged[key] = old_config[key]

    return merged


@lru_cache(maxsize=None)
def get_config() -> Dict:
    """
    Parses the user's configuration, overriding defaults from their profile
    """
    total_config = {
        # Default cannot be set in profile due to the value depending on platform
        "CONFIGS": {},
        "PLATFORM": sys.platform,
    }

    if sys.platform == "win32":
        import ctypes.wintypes

        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value

        __BUF = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(
            None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, __BUF
        )
        total_config["PERSONAL"] = __BUF.value

    for parent in profile_parents():
        path = os.path.join(parent, "defaults.conf")
        if os.path.exists(path):
            total_config = read_config(path, total_config)

    if os.path.exists(env.PORTMOD_CONFIG):
        total_config = read_config(env.PORTMOD_CONFIG, total_config, user=True)
    else:
        create_config_placeholder()

    # Apply environment variables onto config
    for key in __OVERRIDE_KEYS:
        if key in os.environ:
            if key not in total_config.get("PROFILE_ONLY_VARIABLES", []):
                total_config[key] = os.environ[key].split()

    for key in __COLLAPSE_KEYS:
        if key in os.environ:
            if key not in total_config.get("PROFILE_ONLY_VARIABLES", []):
                total_config[key] = collapse_flags(
                    total_config.get(key, set()), os.environ[key].split()
                )

    for key in total_config:
        if key not in __COLLAPSE_KEYS | __OVERRIDE_KEYS:
            if isinstance(total_config[key], str):
                os.environ[key] = total_config[key]

    to_remove = []
    for key in total_config:
        if isinstance(total_config[key], Config):
            conf: Config = total_config[key]
            new_conf = conf
            for key2 in conf.__dict__:
                if isinstance(conf.__dict__[key2], str):
                    new_conf.__dict__[key2] = string.Template(
                        conf.__dict__[key2]
                    ).substitute(total_config)
                if key2 == "path":
                    new_conf.path = os.path.expanduser(new_conf.path)
            total_config["CONFIGS"][key] = new_conf
            to_remove.append(key)
        else:  # All keys can use ${NAME} substitutions to use the final value
            #    instead of the current value of a field
            if isinstance(total_config[key], str):
                total_config[key] = string.Template(total_config[key]).substitute(
                    total_config
                )
            elif isinstance(total_config[key], list):
                for index, elem in enumerate(total_config[key]):
                    if isinstance(elem, str):
                        total_config[key][index] = string.Template(elem).substitute(
                            total_config
                        )
            elif isinstance(total_config[key], set):
                newset = set()
                for elem in total_config[key]:
                    if isinstance(elem, str):
                        newset.add(string.Template(elem).substitute(total_config))
                    else:
                        newset.add(elem)
                total_config[key] = newset

    for key in to_remove:
        del total_config[key]

    return total_config


def config_to_string(config: Dict) -> str:
    """
    Prints the given dictionary config as a string

    The resulting string is suitable for reading by read_config
    """
    lines = []
    for key in sorted(config):
        if isinstance(config[key], set) or isinstance(config[key], list):
            lines.append("{} = {}".format(key, " ".join(sorted(config[key]))))
        else:
            lines.append("{} = {}".format(key, config[key]))
    return "\n".join(lines)
