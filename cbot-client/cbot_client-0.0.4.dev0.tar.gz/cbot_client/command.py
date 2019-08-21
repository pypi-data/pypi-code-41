import argparse
import os

import requests

from cbot_client.new_recipe import new_recipe
from cbot_client.runner import run_create


def run(*args):
    parser = argparse.ArgumentParser(description="", prog="cbot")
    subparsers = parser.add_subparsers(dest='subcommand', help='sub-command help')
    subparsers.required = True

    new_parser = subparsers.add_parser('new', help='Add a new package version')
    new_parser.add_argument("index_path", help='Path to a clone of the cbot index repo')
    new_parser.add_argument("-n", "--name", help='Name of the package')
    new_parser.add_argument("-v", "--version", help='Version of the package')
    new_parser.add_argument("-f", "--folder", help='Folder where the recipe will be')
    new_parser.add_argument("-s", "--url", help='URL to a zip with the sources')

    subparsers.add_parser('setup', help='Installs the conan-center hook in '
                                        'the current conan installation')

    run_parser = subparsers.add_parser('run', help='Runs the conan create of a reference')
    run_parser.add_argument("index_path", help='Path to a clone of the cbot index repo')
    run_parser.add_argument("ref", help='package_name/version. e.g: lib/1.0')
    run_parser.add_argument("-u", "--profile_url", help='A URL to the profile to be downloaded')
    run_parser.add_argument("-p", "--profile", help='Profile name or path')
    try:
        args = parser.parse_args(*args)
        if args.subcommand == "new":
            return new_recipe(args.index_path, args.name, args.version, args.folder, args.url)
        elif args.subcommand == "setup":
            hooks_url = "https://github.com/lasote/hooks.git"
            os.system("conan config install {} -sf hooks -tf hooks".format(hooks_url))
            os.system("conan config set hooks.conan-center")
        elif args.subcommand == "run":
            run_create(args.index_path, args.ref, args.profile, args.profile_url)
    except KeyboardInterrupt:
        print("\nKilled!")
    except Exception as exc:
        print("Error: {}".format(exc))
        exit(-1)


