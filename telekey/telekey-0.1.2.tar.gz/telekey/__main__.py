import os
import click


@click.group()
def cli():
    pass


@cli.command()
@click.argument('directory', type=click.Path(exists=True))
def new(directory):
    print(directory)
    pass


def main():
    cli()

if __name__ == "__main__":
    main()
