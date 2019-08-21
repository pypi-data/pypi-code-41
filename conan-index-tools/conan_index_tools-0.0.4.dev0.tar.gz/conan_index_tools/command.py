import argparse
import os

from conan_index_tools.new_recipe import new_recipe
from conan_index_tools.runner import run_create


def run(*args):
    parser = argparse.ArgumentParser(description="", prog="cit")
    subparsers = parser.add_subparsers(dest='subcommand', help='sub-command help')
    subparsers.required = True

    # 'NEW' COMMAND
    new_parser = subparsers.add_parser('new', help='Add a new package version')
    new_parser.add_argument("index_path", help='Path to a clone of the conan center index fork')
    new_parser.add_argument("-n", "--name", help='Name of the package')
    new_parser.add_argument("-v", "--version", help='Version of the package')
    new_parser.add_argument("-f", "--folder", help='Folder where the recipe will be')
    new_parser.add_argument("-s", "--url", help='URL to a zip with the sources')

    # 'SETUP' COMMAND
    setup_parser = subparsers.add_parser('setup', help='Enable the conan-center hook')
    setup_parser.add_argument("-c", "--clean", action='store_true', default=False,
                              help='Disable the conan-center hook')

    # 'RUN' COMMAND
    run_parser = subparsers.add_parser('run', help='Runs the conan create of a reference')
    run_parser.add_argument("index_path", help='Path to a clone of the conan center index fork')
    run_parser.add_argument("ref", help='package_name/version. e.g: lib/1.0')
    run_parser.add_argument("-u", "--profile_url", help='A URL to the profile to be downloaded')
    run_parser.add_argument("-p", "--profile", help='Profile name or path')
    try:
        args = parser.parse_args(*args)
        if args.subcommand == "new":
            return new_recipe(args.index_path, args.name, args.version, args.folder, args.url)
        elif args.subcommand == "setup":
            if not args.clean:
                hooks_url = "https://github.com/lasote/hooks.git"
                os.system("conan config install {} -sf hooks -tf hooks".format(hooks_url))
                os.system("conan config set hooks.conan-center")
                print("Hook installed")
            else:
                os.system("conan config rm hooks.conan-center")
                print("Hook deactivated")
        elif args.subcommand == "run":
            run_create(args.index_path, args.ref, args.profile, args.profile_url)
    except KeyboardInterrupt:
        print("\nKilled!")
    except Exception as exc:
        print("Error: {}".format(exc))
        exit(-1)


