#! /usr/bin/env python
import importlib
import os

import click

from nicky.utils import COMMANDS_PATH


@click.group()
def cli():
    pass


for i in [f for f in os.listdir(COMMANDS_PATH) if f.find('cd_') == 0]:
    name = i.replace('.py', '')
    module = importlib.import_module('nicky.commands.{}'.format(name))
    cli.add_command(getattr(module, name.replace('cd_', '')))

if __name__ == '__main__':
    cli()
