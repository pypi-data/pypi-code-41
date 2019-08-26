import click
from dep.commands import list_command, install_command

@click.group()
def dependencies():
    """Defines the group for environment commands"""
    pass


@dependencies.command()
@click.option('--name', '-n', required=True)
def install(name):
    
    install_command(name)


@dependencies.command()
@click.option('--out', '-o', help='The output file for the results')
@click.option('--json', '-j', is_flag=True, default=False)
def list(out, json):
    """The command for displaying the current environment

    Args:
        out (str): Optional file name to output the 
        json (bool): Indicates if the output should be in json
    """

    list_command(out, json)