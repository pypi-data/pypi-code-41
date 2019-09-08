# -*- coding: utf-8 -*-

"""Console script for term_frequency."""
import sys
import click


@click.command()
def main(args=None):
    """Console script for term_frequency."""
    click.echo("Replace this message by putting your code into "
               "term_frequency.cli.main")
    click.echo("See click documentation at http://click.pocoo.org/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
