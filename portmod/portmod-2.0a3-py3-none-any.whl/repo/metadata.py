# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

# Helper functions for interacting with repository metadata files.
# Arguments are either a repo path, or mod object.

from typing import Set
import os
import glob
from functools import lru_cache
from portmod.yaml import yaml_load
from portmod.repo.list import read_list
from .usestr import use_reduce
from portmod.globals import env
from portmod.log import err
from ..config import get_config


@lru_cache()
def get_masters(repo_path):
    masters = []
    for repo in env.REPOS:
        if os.path.abspath(os.path.normpath(repo_path)) == os.path.abspath(
            os.path.normpath(repo.location)
        ):
            for master in repo.masters:
                n = next((x for x in env.REPOS if x.name == master), None)
                if n is not None:
                    masters.append(n)
                else:
                    err("Unable to find master {} of repo {}".format(master, repo.name))
    return masters


@lru_cache()
def get_repo_name(path):
    root = get_repo_root(path)
    if root is None:
        return None
    path = os.path.join(root, "profiles", "repo_name")
    if os.path.exists(path):
        with open(path, mode="r") as name_file:
            return name_file.read().strip()
    return None


@lru_cache()
def get_repo_root(path):
    path = os.path.abspath(path)
    # Recursively look for metadata/repo_name to identify root
    if os.path.exists(os.path.join(path, "profiles", "repo_name")):
        return path
    elif os.path.dirname(path) == path:
        # We've reached the root of the FS there is no repo
        return None

    return get_repo_root(os.path.dirname(path))


# Retrieves the list of categories given a path to a repo
@lru_cache()
def get_categories(repo):
    categories = set()
    path = os.path.join(repo, "profiles", "categories")
    if os.path.exists(path):
        categories |= set(read_list(path))
    for master in get_masters(repo):
        categories |= get_categories(master.location)

    return categories


@lru_cache()
def get_archs(repo):
    archs = set()
    path = os.path.join(repo, "profiles", "arch.list")
    if os.path.exists(path):
        archs |= set(read_list(path))

    for master in get_masters(repo):
        archs |= get_archs(master.location)

    return read_list(path)


@lru_cache()
def get_global_use(repo):
    use = {}
    path = os.path.join(repo, "profiles", "use.yaml")
    if os.path.exists(path):
        with open(path, mode="r") as use_file:
            use.update(yaml_load(use_file))

    for master in get_masters(repo):
        use.update(get_global_use(master.location))

    return use


@lru_cache()
def get_profiles():
    profiles = []
    for repo in env.REPOS:
        path = os.path.join(repo.location, "profiles", "profiles.yaml")
        if os.path.exists(path):
            with open(path, mode="r") as use_file:
                repo_profiles = yaml_load(use_file)
                for keyword in repo_profiles:
                    for profile in repo_profiles[keyword]:
                        path = os.path.join(repo.location, "profiles", profile)
                        profiles.append(
                            (path, profile, repo_profiles[keyword][profile])
                        )
    return profiles


# Returns true if the given license is valid
@lru_cache()
def license_exists(repo, name):
    path = os.path.join(repo, "licenses", name)
    if os.path.exists(path):
        return True

    for master in get_masters(repo):
        if license_exists(master.location, name):
            return True

    return False


@lru_cache()
def has_eula(mod):
    groups = get_license_groups(get_repo_root(mod.FILE))
    return mod.LICENSE in groups.get("EULA")


# returns the full content of the named license
@lru_cache()
def get_license(repo, name):
    path = os.path.join(repo, "licenses", name)
    if os.path.exists(path):
        with open(path, mode="r") as license_file:
            return license_file.read()
    else:
        for master in get_masters(repo):
            license = get_license(master.location, name)
            if license is not None:
                return license

        raise Exception("Nonexistant license: {}".format(name))


# returns a map of group names to sets of licenses
@lru_cache()
def get_license_groups(repo):
    result = {}
    path = os.path.join(repo, "profiles", "license_groups.yaml")
    if os.path.exists(path):
        with open(path, mode="r") as group_file:
            groups = yaml_load(group_file)

        for name, values in groups.items():
            if values is not None:
                result[name] = set(values.split())
            else:
                result[name] = set()

    def substitute(group: str):
        groups = []
        for license in result[group]:
            if license.startswith("@"):
                groups.append(license)
        for subgroup in groups:
            result[group].remove(subgroup)
            substitute(subgroup.lstrip("@"))
            result[group] |= result[subgroup.lstrip("@")]

    for group in result:
        substitute(group)

    for master in get_masters(repo):
        result.update(get_license_groups(master.location))

    return result


# returns true if the user's ACCEPTS_LICENSE accepts the given mod
# For a license to be accepted, it must be both listed, either explicitly,
#   part of a group, or with the * wildcard  and it must not be blacklisted
#  by a license or license group prefixed by a -
def is_license_accepted(mod):
    license_groups = get_license_groups(get_repo_root(mod.FILE))

    ACCEPT_LICENSE = get_config()["ACCEPT_LICENSE"]

    def accepted(group):
        if isinstance(group, str):
            allowed = False
            # Check if license is allowed by anything in ACCEPT_LICENSE
            for license in ACCEPT_LICENSE:
                if license.startswith("-") and (
                    license == group
                    or (license[1] == "@" and group in license_groups[license[2:]])
                ):
                    # not allowed if matched by this
                    return False
                if license == "*":
                    allowed = True
                if license.startswith("@") and group in license_groups[license[1:]]:
                    allowed = True
            return allowed
        elif group[0] == "||":
            return any(accepted(license) for license in group)
        else:
            return all(accepted(license) for license in group)

    enabled, disabled = mod.get_use()
    return accepted(use_reduce(mod.LICENSE, enabled, disabled, opconvert=True))

    # TODO: implement mod-specific license acceptance via mod.license config file


# Loads the metadata file for the given mod
@lru_cache()
def get_mod_metadata(mod):
    path = os.path.join(os.path.dirname(mod.FILE), "metadata.yaml")
    if not os.path.exists(path):
        return None

    with open(path, mode="r") as metadata_file:
        metadata = yaml_load(metadata_file)

    return metadata


# Loads the metadata file for the given category
@lru_cache()
def get_category_metadata(repo, category):
    path = os.path.join(repo, category, "metadata.yaml")

    if os.path.exists(path):
        with open(path, mode="r") as metadata_file:
            metadata = yaml_load(metadata_file)
        return metadata

    for master in get_masters(repo):
        metadata = get_category_metadata(master.location, category)
        if metadata is not None:
            return metadata

    return None


@lru_cache()
def get_use_expand(repo: str) -> Set[str]:
    """Returns all possible use expand values for the given repository"""
    groups = set()
    for file in glob.glob(os.path.join(repo, "profiles", "desc", "*.yaml")):
        groups.add(os.path.basename(file).upper())
    for master in get_masters(repo):
        groups |= get_use_expand(master.location)

    return groups


@lru_cache()
def check_use_expand_flag(repo: str, variable: str, flag: str) -> bool:
    """
    Returns true if the given use flag is declared
    in a USE_EXPAND desc file for the given variable
    """
    print(repo, variable, flag)
    path = os.path.join(repo, "profiles", "desc", variable.lower() + ".yaml")
    if os.path.exists(path):
        with open(path, mode="r") as file:
            if flag in yaml_load(file):
                return True

    for master in get_masters(repo):
        if check_use_expand_flag(master.location, variable, flag):
            return True

    return False
