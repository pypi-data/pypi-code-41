import socket

import click
import requests
import requirements
from flask import Flask, redirect

from packaging.specifiers import SpecifierSet
from packaging.version import Version

MAIN_PYPI = 'https://pypi.org/simple/'
JSON_URL = 'https://pypi.org/pypi/{package}/json'

PACKAGE_HTML = """
<!DOCTYPE html>
<html>
  <head>
    <title>Links for {package}</title>
  </head>
  <body>
    <h1>Links for {package}</h1>
{links}
  </body>
</html>
"""


@click.command()
@click.argument('requirements_file')
@click.option('--port', default=None)
def main(requirements_file, port):

    app = Flask(__name__)

    INDEX = requests.get(MAIN_PYPI).content

    SPECIFIERS = {}
    with open(requirements_file, 'r') as fd:
        for req in requirements.parse(fd):
            if req.specs:
                SPECIFIERS[req.name] = SpecifierSet(','.join([''.join(spec) for spec in req.specs]))

    @app.route("/")
    def main_index():
        return INDEX

    @app.route("/<package>/")
    def package_info(package):

        if package not in SPECIFIERS:
            return redirect(MAIN_PYPI + package)

        package_index = requests.get(JSON_URL.format(package=package)).json()

        release_links = ""
        for version, release in package_index['releases'].items():
            if Version(version) in SPECIFIERS[package]:
                for file in release:
                    if file['requires_python'] is None:
                        release_links += '    <a href="{url}#sha256={sha256}">{filename}</a><br/>\n'.format(url=file['url'], sha256=file['digests']['sha256'], filename=file['filename'])
                    else:
                        rp = file['requires_python'].replace('>', '&gt;')
                        release_links += '    <a href="{url}#sha256={sha256}" data-requires-python="{rp}">{filename}</a><br/>\n'.format(url=file['url'], sha256=file['digests']['sha256'], rp=rp, filename=file['filename'])

        return PACKAGE_HTML.format(package=package, links=release_links)

    host = socket.gethostbyname('localhost')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    if port is None:
        port = sock.getsockname()[1]
    sock.close()

    app.run(host=host, port=port)
