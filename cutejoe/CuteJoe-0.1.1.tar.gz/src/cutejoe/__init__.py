import click

from .commands.changelog import changelog
from .commands.config_file import config_file


@click.group()
def cli():
    pass  # pragma: no cover


cli.add_command(changelog)
cli.add_command(config_file)
