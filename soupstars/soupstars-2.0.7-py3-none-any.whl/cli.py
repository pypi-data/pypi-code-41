"""
Command line interface for SoupStars
"""

# TODO: functions for normalizing module names (adding .py when necessary, and
# removing .py when necessary)
# TODO: normalize printing functions. The client should always return a response
# object and the .json fields should be printed with click.secho

import click
import json
import os
import sys
import textwrap

from soupstars.core import SoupStar
from soupstars.client import Client
from soupstars import __version__


@click.group()
def cli():
    """
    CLI to interact with SoupStars cloud.
    """

    pass


@cli.command()
def ls():
    """
    Show the parsers uploaded to SoupStars cloud
    """

    client = Client()
    resp = client.ls()
    print(resp.json())


@cli.command()
def health():
    """
    Print the status of the SoupStars api
    """

    resp = Client().health()
    print(resp.json())


@cli.command()
def register():
    """
    Register a new account on SoupStars cloud
    """

    email = input('Email: ')
    password = input('Password: ')

    client = Client()
    resp = client.register(email=email, password=password)
    if resp.ok:
        client.token = resp.json()['token']
        client.update_config()
    print(resp.json())


@cli.command()
def whoami():
    """
    Print the email address of the current user
    """

    client = Client()
    resp = client.profile()
    print(resp.json())


@cli.command()
def config():
    """
    Print the configuration used by the client
    """

    client = Client()
    print(client.config())


@cli.command()
@click.option('--module', '-m', required=True, help="Name of the parser to create")
@click.option('--force/--no-force', default=False, help="Overwrite an existing file")
def create(module, force):
    """
    Create a new parser from a template
    """

    if module[-3:] != '.py':
        module = module + ".py"

    if os.path.exists(module) and not force:
        raise FileExistsError(f"{module} already exists. Use --force to overwrite.")

    template = textwrap.dedent("""\
    from soupstars import parse, SoupStar

    url = "https://corbettanalytics.com/"

    @parse
    def h1(soup):
        return soup.h1.text

    if __name__ == "__main__":
        print(SoupStar(__name__).to_dict())

    """)

    with open(module, 'w') as o:
        o.write(template)
        print("Done")


@cli.command()
@click.option('--module', '-m', required=True, help="Name of the parser to push")
def push(module):
    """
    Push a parser to SoupStars cloud
    """

    client = Client()
    resp = client.push(module)


@cli.command()
@click.option('--module', '-m', required=True, help="Name of the parser to pull")
def pull(module):
    """
    Pull a parser from SoupStars cloud into a local module
    """

    client = Client()
    resp = client.pull(module)
    data = resp.json()
    with open(data['name'], 'w') as o:
        o.write(data['module'])
    print(f"Wrote {data['name']}")


@cli.command()
@click.option('--module', '-m', required=True, help="Name of the parser to create")
def run(module):
    """
    Run a parser on SoupStars cloud
    """

    client = Client()
    resp = client.run(module)
    print(resp.json())


@cli.command()
@click.option('--module', '-m', required=True, help="Name of the parser to show")
def show(module):
    """
    Show the contents of a parser on SoupStars cloud
    """

    client = Client()
    resp = client.pull(module)
    data = resp.json()
    print(data['module'])


@cli.command()
@click.option('--module', '-m', required=True, help="Name of the parser to test")
def test(module):
    """
    Test running a parser locally
    """

    if module[-3:] == ".py":
        module = module[:-3]

    print(f"Testing module {module}")

    soupstar = SoupStar(module)
    print(soupstar.to_dict())


@cli.command()
def version():
    """
    Print the SoupStars version in use
    """

    print(__version__, f"(Python {sys.version})".replace('\n', ''), sep=", ")
