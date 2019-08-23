import click
import os
import sys
import logging
from urllib.parse import urlparse
from . import __version__
from .project import Project
from .package import Package


logger = logging.getLogger(__name__)


# click entrypoint
@click.group()
@click.option('--log', type=click.Choice(['debug', 'info', 'warning', 'error']), default='warning',
    help='Set the level of logs.'
)
def main(log):

    """Startin'Blox installer"""

    # set log level
    numeric_level = getattr(logging, log.upper(), None)
    logging.basicConfig(level=numeric_level)


@main.command()
@click.argument('name', nargs=1)
@click.argument('directory', required=False)
@click.option('--production', is_flag=True, default=False, help='Use a production template')
def startproject(name, production, directory):

    """Start a new startin'blox project"""

    # set absolute path to project directory
    create_dir = False
    if directory:
        directory = os.path.abspath(directory)
    else:
        # set a directory from project name in pwd
        directory = os.path.join(os.getcwd(), name)
        create_dir = True

    project = Project(name, directory)
    project.create(production, create_dir)


@main.command()
@click.argument('name', nargs=1)
@click.argument('directory', required=False)
def install(name, directory):

    """Initialize a startin'blox project"""

    # set absolute path to project directory
    if directory:
        directory = os.path.abspath(directory)
    else:
        # get path from current dir
        directory = os.getcwd()

    project = Project(name, directory)
    project.install()
    project.load()


@main.command()
@click.argument('name', nargs=1)
@click.argument('directory', required=False)
def startpackage(name, directory):

    try:

        """Create a new startin'blox package"""

        # set absolute path to package directory (given directory is the project path)
        if directory:
            directory = os.path.join(os.path.abspath(directory), name)
        else:
            # get path from current dir
            directory = os.path.join(os.getcwd(), name)

        package = Package(name, directory)
        package.create()

    except:
        sys.exit(1)

@main.command()
def version():
    """Print module version"""
    click.echo(__version__)
