from aiohttp import web

import click

from web.core import app


@click.command()
@click.option('--port', type=int, default=5000, help='Port to run app on')
def main(port):
    web.run_app(app, port=port)
