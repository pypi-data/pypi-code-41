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
import getpass
from pygments import highlight, lexers, formatters

from soupstars.core import SoupStar
from soupstars.client import Client
from soupstars import __version__


def jsonify(data):
    formatted_json = json.dumps(data, sort_keys=True, indent=2)
    colorful_json = highlight(
        formatted_json,
        lexers.JsonLexer(),
        formatters.TerminalFormatter(style="autumn")
    )
    print(colorful_json)


@click.group()
def cli():
    """
    CLI to interact with SoupStars cloud.
    """

    pass


@cli.command()
def login():
    """
    Log in with an existing email
    """

    client = Client()
    email = input('Email: ')
    password = getpass.getpass(prompt='Password: ')

    resp = client.login(email=email, password=password)

    if resp.ok:
        client.token = resp.json()['token']
        client.update_config()

    jsonify(resp.json())


@cli.command()
def ls():
    """
    Show the parsers uploaded to SoupStars cloud
    """

    client = Client()
    resp = client.ls()
    jsonify(resp.json())


@cli.command()
def health():
    """
    Print the status of the SoupStars api
    """

    resp = Client().health()
    jsonify(resp.json())


@cli.command()
def register():
    """
    Register a new account on SoupStars cloud
    """

    email = input('Email: ')
    password = getpass.getpass(prompt='Password: ')
    password2= getpass.getpass(prompt='Confirm password: ')

    if password != password2:
        print("Passwords did not match.")
        return

    client = Client()
    resp = client.register(email=email, password=password)

    if resp.ok:
        client.token = resp.json()['token']
        client.update_config()

    jsonify(resp.json())


@cli.command()
def whoami():
    """
    Print the email address of the current user
    """

    client = Client()
    resp = client.profile()
    jsonify(resp.json())


@cli.command()
def config():
    """
    Print the configuration used by the client
    """

    client = Client()
    jsonify(client.config())


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
        jsonify({"state": "done", "module": module})


@cli.command()
@click.option('--module', '-m', required=True, help="Name of the parser to push")
def push(module):
    """
    Push a parser to SoupStars cloud
    """

    client = Client()
    resp = client.push(module)
    jsonify(resp.json())


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
    jsonify({"state": "done", "response": data})


@cli.command()
@click.option('--module', '-m', required=True, help="Name of the parser to create")
def run(module):
    """
    Run a parser on SoupStars cloud
    """

    client = Client()
    resp = client.run(module)
    jsonify(resp.json())


@cli.command()
@click.option('--module', '-m', required=True, help="Name of the parser to show")
def show(module):
    """
    Show the contents of a parser on SoupStars cloud
    """

    client = Client()
    resp = client.pull(module)
    jsonify(resp.json())


@cli.command()
@click.option('--module', '-m', required=True, help="Name of the parser to test")
def test(module):
    """
    Test running a parser locally
    """

    if module[-3:] == ".py":
        module = module[:-3]

    if '.' not in sys.path:
        sys.path.append('.')

    soupstar = SoupStar(module)
    jsonify(soupstar.to_dict())


@cli.command()
def version():
    """
    Print the SoupStars version in use
    """

    result = {
        "version": __version__,
        "python": f"{sys.version})".replace('\n', '')
    }

    jsonify(result)


@cli.command()
@click.option('--module', '-m', required=True, help="Name of the parser to test")
def results(module):
    """
    Print results of a parser
    """

    client = Client()
    resp = client.results(module)
    jsonify(resp.json())
