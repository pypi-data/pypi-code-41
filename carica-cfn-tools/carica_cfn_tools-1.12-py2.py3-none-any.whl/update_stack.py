"""
Creates a change set that updates an existing CloudFormation, then opens a web browser
so it can be manually reviewed and executed.
"""
import sys

import click

from carica_cfn_tools.stack_config import Stack, CaricaCfnToolsError


@click.command()
@click.argument('stack_config_file')
def main(stack_config_file):
    try:
        config = Stack(stack_config_file)
        config.create_change_set(change_set_type='UPDATE')
    except CaricaCfnToolsError as e:
        print('ERROR: ' + str(e), file=sys.stderr)
        sys.exit(1)
