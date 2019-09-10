import click
from scripts.nm_tunnel_setup import nm_tunnel_setup


@click.group()
def cli():
    pass


@cli.command()
def hello():
    """Example script."""
    click.echo('Hello World!')


@cli.command()
def tunnel_setup():
    """Add tunnel config to NetworkManager"""
    nm_tunnel_setup()
