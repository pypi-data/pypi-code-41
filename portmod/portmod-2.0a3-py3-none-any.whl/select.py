# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
CLI to select various configuration options

Currently just profiles
"""

import argparse
import os
import sys
import traceback
from .log import err
from .repo.metadata import get_profiles
from .colour import lblue, bright, green
from .globals import env


def main():
    """
    Main function for the omwselect executable
    """
    parser = argparse.ArgumentParser(
        description="Command line interface to select between options"
    )
    parser.add_argument("--debug", help="Enables debug traces", action="store_true")
    subparsers = parser.add_subparsers()
    profile = subparsers.add_parser("profile", help="manage the profile symlink")
    profile_subparsers = profile.add_subparsers()
    profile_list = profile_subparsers.add_parser("list", help="list available profiles")
    profile_set = profile_subparsers.add_parser(
        "set", help="set a new profile symlink target"
    )
    profile_set.add_argument("NUM", help="profile number")
    profile_show = profile_subparsers.add_parser(
        "show", help="Show the current profile symlink target"
    )

    def get_profile():
        linkpath = os.path.join(env.PORTMOD_CONFIG_DIR, "profile")
        if os.path.exists(linkpath) and os.path.islink(linkpath):
            return os.readlink(linkpath).split("profiles")[-1].lstrip(os.path.sep)
        return None

    def list_func(args):
        profiles = get_profiles()
        padding = len(str(len(profiles)))
        print(bright(green("Available profile symlink targets:")))
        for index, (_, profile, stability) in enumerate(profiles):
            selected = ""
            if get_profile() == profile:
                selected = lblue("*")
            print(
                "  {} {} ({})".format(
                    bright("[" + str(index) + "]"),
                    " " * (padding - len(str(index))) + profile,
                    stability,
                ),
                selected,
            )

    def set_func(args):
        os.makedirs(env.PORTMOD_CONFIG_DIR, exist_ok=True)
        linkpath = os.path.join(env.PORTMOD_CONFIG_DIR, "profile")
        if os.path.exists(linkpath):
            os.unlink(linkpath)
        (path, _, _) = get_profiles()[int(args.NUM)]
        os.symlink(path, linkpath)

    def show_func(args):
        linkpath = os.path.join(env.PORTMOD_CONFIG_DIR, "profile")
        print(bright(green("Current {} symlink:".format(linkpath))))
        print(
            "  "
            + bright(os.readlink(linkpath).split("profiles")[-1].lstrip(os.path.sep))
        )

    def profile_help(args):
        profile.print_help()

    profile.set_defaults(func=profile_help)
    profile_list.set_defaults(func=list_func)
    profile_set.set_defaults(func=set_func)
    profile_show.set_defaults(func=show_func)

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        exit(2)

    if args.debug:
        env.DEBUG = True
    try:
        args.func(args)
    except Exception as e:
        traceback.print_exc()
        err("{}".format(e))
        exit(1)
