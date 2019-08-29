import argparse
import subprocess
import sys

from . file_io import load_env, save_env, env_file


def install():
    parser = argparse.ArgumentParser(
                description='Install packages in the active environment')
    parser.add_argument('--pip', action='store_true',
                        help="Install packages from PyPI with pip")
    parser.add_argument('package_spec', nargs='+')
    parser.add_argument('-c', nargs='?', dest='channel',
                        help="Conda channel for packages")
    
    args = parser.parse_args(sys.argv[2:])

    try:
        env = load_env()
    except FileNotFoundError:
        print(f"This environment isn't managed by Abode, use conda instead.")
        return None

    if args.pip:
        for each in env['dependencies']:
            try:
                pip_packages = each['pip']
            except TypeError:
                continue
            # Found the pip dependencies
            pip_packages.extend(args.package_spec)
    else:
        env['dependencies'].extend(args.package_spec)

    if args.channel:
        env['channels'].insert(0, args.channel)

    save_env(env)

    subprocess.run(['conda', 'env', 'update', '-f', env_file(env['name'])])