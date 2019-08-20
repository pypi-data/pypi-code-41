import click

from DatastoreClient.Client import Client


def config():
    pass


@click.command()
@click.option("create", help="Number of greetings.")
@click.option("query", prompt="Your name", help="The person to greet.")
def raw():
    pass


def model():
    pass


def weight():
    pass


def attachment():
    pass


def dataset():
    pass


@click.command()
@click.option("--count", default=1, help="Number of greetings.")
@click.option("--name", prompt="Your name", help="The person to greet.")
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for _ in range(count):
        click.echo("Hello, %s!" % name)


if __name__ == "__main__":
    hello()
