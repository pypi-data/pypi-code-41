# -*- coding: utf-8 -*-

import sys

import click

from . import aws_key_formatter
from .__version__ import __version__


@click.command()
@click.version_option(version=__version__, prog_name="aws-key-formatter")
@click.argument("formatter", type=click.Choice(["redshift", "env"]))
@click.option(
    "-p", "--profile", default="default", show_default=True, help="AWS CLI Profile name"
)
@click.option(
    "--token/--no-token",
    " -t/",
    default=False,
    show_default=True,
    help="Include AWS Session Token?",
)
def main(formatter: str, profile: str, token: bool):
    """Console script for aws_key_formatter."""
    formatted_str = aws_key_formatter.main(formatter, profile, token)
    click.echo(formatted_str)

    return 0


if __name__ == "__main__":
    sys.exit(main())
