# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
CLI for interacting with individual pybuild files
"""

import sys
import argparse
import traceback
from .globals import env
from .repo.loader import load_file
from .repo.download import download_mod
from .log import err
from .mod import install_mod, remove_mod
from .main import pybuild_validate, pybuild_manifest


def main():
    """
    Main function for pybuild executable.
    """
    parser = argparse.ArgumentParser(
        description="Command line interface to interact with pybuilds"
    )
    parser.add_argument("pybuild_file", metavar="<pybuild file>")
    parser.add_argument(
        "command",
        metavar="<command>",
        nargs="+",
        choices=[
            "manifest",
            "fetch",
            "unpack",
            "prepare",
            "install",
            "qmerge",
            "merge",
            "unmerge",
            "validate",
        ],
    )
    parser.add_argument("--debug", help="Enables debug traces", action="store_true")
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()

    env.ALLOW_LOAD_ERROR = False

    if args.debug:
        env.DEBUG = True
    try:
        for command in args.command:
            if command == "manifest":
                pybuild_manifest(args.pybuild_file)
            elif command == "fetch":
                mod = load_file(args.pybuild_file)
                sources = download_mod(mod)
                if not sources and not mod.NO_DOWNLOAD:
                    print("Unable to fetch mod archives. Aborting.")
                    exit(1)
            elif command == "merge":
                mod = load_file(args.pybuild_file)
                install_mod(mod)
            elif command == "unmerge":
                remove_mod(mod)
            elif command == "validate":
                pybuild_validate(args.pybuild_file)
    except FileNotFoundError as e:
        if env.DEBUG:
            traceback.print_exc()
        err("{}".format(e))
    except Exception as e:
        traceback.print_exc()
        err("{}".format(e))
