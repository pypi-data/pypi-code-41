"""
CLI App for MonicaCRM. Intended primarily for bulk imports of CSV records.

Not yet, uh, anything
"""
import click


@click.command()
@click.argument('names', nargs=-1)
def main(names):
    click.echo(repr(names))
