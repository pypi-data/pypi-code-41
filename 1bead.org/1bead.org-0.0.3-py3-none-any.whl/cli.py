from aiohttp import web

from web.core import app


def main():
    web.run_app(app, port=80)
