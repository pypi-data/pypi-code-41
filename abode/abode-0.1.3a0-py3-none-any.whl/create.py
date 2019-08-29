import argparse
import subprocess
import sys

from . file_io import save_env, env_file, import_env

def create():
    parser = argparse.ArgumentParser(
            description='Create a new environment')
    parser.add_argument('-n', '--name', type=str, help="Name of environment")
    parser.add_argument('package_spec', nargs='*', help="Packages to install on creation")
    parser.add_argument('-f', '--file', type=str, help="Create environment from environment file")
    args = parser.parse_args(sys.argv[2:])

    if len(args.package_spec) == 0:
        args.package_spec.append('python=3')

    if args.file:
        env = import_env(args.file)
    else:
        env = {'name': args.name,
               'channels': ['defaults'],
               'dependencies': ['pip', {'pip':['abode', 'pyyaml']}]}
        env['dependencies'].extend(args.package_spec)
        save_env(env)

    subprocess.run(['conda', 'env', 'create', '-f', env_file(env['name'])])

    return True
