# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Quality assurance for the mod repo
"""

import os
import sys
import argparse
import traceback
import glob
import re
from portmod.globals import env
from portmod.yaml import yaml_load, Person, Group
from portmod.main import pybuild_validate, pybuild_manifest
from portmod.repo.metadata import get_categories, get_repo_root, license_exists
from .repo.manifest import verify_manifest, ManifestMissing
from .repo.loader import load_file
import portmod.log as log
from portmod.repo.list import read_list
from .repos import Repo
from .repo.atom import Atom


def manifest_check(repo_root, err):
    # Run verify manifest on every pybuild in repo
    for category in get_categories(repo_root):
        for file in glob.glob(os.path.join(repo_root, category, "*", "*.pybuild")):
            try:
                mod = load_file(file)
                verify_manifest(mod)
            except (ManifestMissing, FileNotFoundError) as e:
                err(f"{e} - in {file}")
            except Exception as e:
                traceback.print_exc()
                err(f"{e} - in {file}")


def scan(repo_root, err):
    # Run pybuild validate on every pybuild in repo
    for category in get_categories(repo_root):
        for directory in glob.glob(os.path.join(repo_root, category, "*")):
            if (
                os.path.isdir(directory)
                and Atom(os.path.basename(directory)).MV is not None
            ):
                err(f"Mod name {directory} must not end in a version")
        for file in glob.glob(os.path.join(repo_root, category, "*", "*.pybuild")):
            try:
                pybuild_validate(file)
            except Exception as e:
                traceback.print_exc()
                err("{}".format(e))

    # Check files in metadata and profiles.
    # These may not exist, as they might be inherited from another repo instead

    # Check profiles/arch.list
    path = os.path.join(repo_root, "profiles", "arch.list")
    if os.path.exists(path):
        archs = read_list(path)
        for arch in archs:
            if " " in arch:
                err(
                    'arch.list: in entry "{}". '
                    "Architectures cannot contain spaces".format(arch)
                )

    # Check profiles/categories
    path = os.path.join(repo_root, "profiles", "categories")
    if os.path.exists(path):
        lines = read_list(path)
        for category in lines:
            if " " in category:
                err(
                    'categories.list: in category "{}". '
                    "Categories cannot contain spaces".format(category)
                )

    # Check metadata/groups.yaml
    path = os.path.join(repo_root, "metadata", "groups.yaml")
    if os.path.exists(path):
        with open(path, mode="r") as file:
            groups = yaml_load(file)
            for name, group in groups.items():
                if "desc" not in group:
                    err('groups.yaml: Group "{}" is missing "desc" field'.format(name))
                if "members" not in group:
                    err('Group "{}" in "{}" is missing "desc" field'.format(name, path))
                elif group.get("members") is not None:
                    for member in group.get("members"):
                        if type(member) is not Person and type(member) is not Group:
                            err(
                                'groups.yaml: Invalid entry "{}" '
                                'in members of group "{}"'.format(member, name)
                            )

    # Check metadata/license_groups.yaml
    # All licenses should exist in licenses/LICENSE_NAME
    path = os.path.join(repo_root, "profiles", "license_groups.yaml")
    if os.path.exists(path):
        with open(path, mode="r") as file:
            groups = yaml_load(file)
            for key, value in groups.items():
                if value is not None:
                    for license in value.split():
                        if not license_exists(repo_root, license) and not (
                            license.startswith("@")
                        ):
                            err(
                                'license_groups.yaml: License "{}" in group {} '
                                "does not exist in licenses directory".format(
                                    license, key
                                )
                            )

    # Check profiles/repo_name
    path = os.path.join(repo_root, "profiles", "repo_name")
    if os.path.exists(path):
        lines = read_list(path)
        if len(lines) == 0:
            err("repo_name: profiles/repo_name cannot be empty")
        elif len(lines) > 1:
            err(
                "repo_name: Extra lines detected. "
                "File must contain just the repo name."
            )
        elif " " in lines[0]:
            err("repo_name: Repo name must not contain spaces.")

    # Check profiles/use.yaml
    path = os.path.join(repo_root, "profiles", "use.yaml")
    if os.path.exists(path):
        with open(path, mode="r") as file:
            groups = yaml_load(file)
            for _, desc in groups.items():
                if not isinstance(desc, str):
                    err(f'use.yaml: Description "{desc}" is not a string')

    # Check profiles/profiles.yaml
    path = os.path.join(repo_root, "profiles", "profiles.yaml")
    if os.path.exists(path):
        with open(path, mode="r") as file:
            keywords = yaml_load(file)
            for keyword, profiles in keywords.items():
                if keyword not in archs:
                    err(
                        f"profiles.yaml: keyword {keyword} "
                        "was not declared in arch.list"
                    )
                for profile in profiles:
                    if not isinstance(profile, str):
                        err('profiles.yaml: Profile "{profile}" is not a string')
                    path = os.path.join(repo_root, "profiles", profile)
                    if not os.path.exists(path):
                        err(f"profiles.yaml: Profile {path} does not exist")

    for filename in glob.glob(os.path.join(repo_root, "profiles", "desc", "*.yaml")):
        with open(filename, mode="r") as file:
            entries = yaml_load(file)
            for entry in dict(entries):
                if not re.match("[A-Za-z0-9][A-Za-z0-9+_-]*", entry):
                    err(
                        f"USE_EXPAND flag {entry} in {file} contains invalid characters"
                    )


def main():
    """
    Main function for the inquisitor executable
    """
    parser = argparse.ArgumentParser(
        description="Quality assurance program for the mod repository"
    )
    parser.add_argument(
        "mode",
        metavar="[mode]",
        nargs="?",
        choices=["manifest", "manifest-check", "scan"],
        help='Mode in which to run. One of "manifest", "manifest-check", "scan". '
        'Default is "scan"',
    )
    parser.add_argument("--debug", help="Enables debug traces", action="store_true")

    args = parser.parse_args()

    repo_root = get_repo_root(os.getcwd())

    error = False
    env.ALLOW_LOAD_ERROR = False

    def err(string: str):
        nonlocal error
        log.err(string)
        error = True

    if repo_root is None:
        err(
            "Cannot find repository for the current directory. "
            "Please run from within the repository you wish to inspect"
        )

    # Register repo in case it's not already in repos.cfg
    REAL_ROOT = os.path.realpath(repo_root)
    if not any([REAL_ROOT == os.path.realpath(repo.location) for repo in env.REPOS]):
        sys.path.append(os.path.join(repo_root))
        env.REPOS.append(
            Repo(
                os.path.basename(repo_root), repo_root, False, None, None, ["openmw"], 0
            )
        )

    if args.debug:
        env.DEBUG = True
    if args.mode is None or args.mode == "scan":
        scan(repo_root, err)
        manifest_check(repo_root, err)
    elif args.mode == "manifest":
        # Run pybuild manifest on every pybuild in repo
        for category in get_categories(repo_root):
            for file in glob.glob(os.path.join(repo_root, category, "*", "*.pybuild")):
                try:
                    pybuild_manifest(file)
                except Exception as e:
                    traceback.print_exc()
                    err("{}".format(e))
    elif args.mode == "manifest-check":
        manifest_check(repo_root, err)

    if error:
        exit(1)
