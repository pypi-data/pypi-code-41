import argparse
import subprocess
import sys

from . file_io import load_env, save_env, env_file

def list():
    parser = argparse.ArgumentParser(
                description='List installed packages')
    parser.add_argument('-f', '--file', action='store_true',
                        help="List packages maintained in the environment file.")
    
    args = parser.parse_args(sys.argv[2:])

    if args.file:
        try:
            env = load_env()
        except FileNotFoundError:
            print(f"This environment isn't managed by Abode, so file doesn't exist.")
            return None
        
        filename = env_file(env['name'])
        with open(filename, 'r') as f:
                contents = f.read()

        print(contents)
        return
    
    subprocess.run(['conda', 'list'])


    