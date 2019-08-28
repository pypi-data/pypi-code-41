import argparse
import logging
import os

from bmcsf.commands.configure import ConfigureCommand
from bmcsf.commands.down import DownCommand
from bmcsf.commands.list_servers import ListCommand
from bmcsf.commands.up import UpCommand

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    config_dir = os.path.join(os.path.expanduser('~'), '.config', 'bmcsf')
    if not os.path.isdir(config_dir):
        os.makedirs(config_dir)

    parser = argparse.ArgumentParser('bmcsf', description='MINECRAFT SERVER, FAST!')

    parser.add_argument('command', type=str)
    parser.add_argument('--alias', type=str, action='store', default='mcsf_Default')

    args = parser.parse_args()

    command = {
        'up': UpCommand,
        'down': DownCommand,
        'configure': ConfigureCommand,
        'list': ListCommand
    }

    command[args.command]().handle(args)
