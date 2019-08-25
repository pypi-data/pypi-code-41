#!/usr/bin/env python

import click
from env.commands import environment

@click.group()
def cli():
    """Entry point for the cli"""
    pass

cli.add_command(environment)

if __name__ == '__main__':
    """Enables CLI to be run directly"""
    cli()
