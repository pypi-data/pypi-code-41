"""Generate configuration file"""
import os

import click

from cutejoe.helpers import Config, read_text_file, save_text_file


@click.command()
@click.option("--folder", default=".", help="Folder to save config file")
def config_file(folder):
    """Generate configuration file."""
    file_name = ".cutejoe.yml"  # TODO Change to settings file

    file_path = os.path.join(folder, file_name)

    if os.path.exists(file_path):
        click.echo("Config file already exists")
        return

    default_file_path = Config.get_default_file_path()
    content = read_text_file(default_file_path)
    save_text_file(file_path, content)

    click.echo("File created")
