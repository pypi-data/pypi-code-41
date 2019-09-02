import os
import click


@click.group()
def cli():
    pass


@cli.command()
@click.argument('botname', type=str)
def newbot(botname):
    print(os.getcwd())
    pass


def main():
    cli()

if __name__ == "__main__":
    main()
