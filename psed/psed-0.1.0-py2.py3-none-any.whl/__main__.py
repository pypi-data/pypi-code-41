"""CLI utility for text search / replace."""
import sys

import click

from .logger import Logger
from .psed import Psed


@click.command()
@click.option(
    "-i", "--input", help="Path to the input file / directory.", required=True
)
@click.option("-f", "--find", help="String to find.", multiple=True)
@click.option("-r", "--replace", help="String to replace.")
@click.option(
    "--inplace", help="Modify the file(s) in place.", default=False, is_flag=True
)
@click.option("-v", "--verbose", count=True, help="Increase verbosity.")
@click.version_option(version=None)
def main(**kwargs):
    """Console script for psed."""
    Logger.set_verbosity(kwargs.pop("verbose", 0))
    psed = Psed(**kwargs)
    psed.run()


if __name__ == "__main__":
    sys.exit(main(prog_name="psed"))  # pragma: no cover
