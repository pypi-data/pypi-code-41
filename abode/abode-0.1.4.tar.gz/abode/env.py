import argparse
import subprocess
import sys
import textwrap

from . import file_io

def env_list():
    print("# Environments managed by Abode:")
    print("#")
    envs = file_io.env_files()
    for env in envs:
        env_name = env.split('.')[0]
        print(f"{env_name:30s}{file_io.env_file(env_name)}")
    return

def env():
    parser = argparse.ArgumentParser(
                description='Manage environments created by Abode. ')
    parser.add_argument('command', help="abode env command, such as list")

    args = parser.parse_args(sys.argv[2:3])

    available_commands = {'list': env_list}

    command = args.command
    if command not in available_commands:
        print(f"Command 'abode env {command}' doesn't exist. Check available commands with abode env -h")
        return
    else:
        available_commands[command]()
        return