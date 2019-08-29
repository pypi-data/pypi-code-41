import argparse
import subprocess
import sys

from . file_io import load_env, env_file


def update():
    parser = argparse.ArgumentParser(
                description='Update packages in the active environment')

    parser.add_argument('package_spec', nargs='*', help="Specific packages and versions to update")
    
    args = parser.parse_args(sys.argv[2:])

    if args.package_spec: 
        raise NotImplementedError("Updating specific packages not supported yet.")

    try:
        env = load_env()
    except FileNotFoundError:
        print(f"This environment isn't managed by Abode, use conda instead.")
        return None

    subprocess.run(['conda', 'env', 'update', '-f', env_file(env['name'])])