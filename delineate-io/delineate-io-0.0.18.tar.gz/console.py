#!/usr/bin/env python

import click
from dep.click import dependencies
from var.click import variables

@click.group()
def cli():
    """Entry point for the cli"""
    pass

cli.add_command(dependencies)
cli.add_command(variables)

if __name__ == '__main__':
    """Enables CLI to be run directly"""
    cli()
