import os
import click

from distutils.dir_util import copy_tree


@click.group()
def cli():
    pass


@cli.command()
@click.argument('botname', type=str)
def newbot(botname):
    project_dir = os.path.join(os.getcwd(), botname)
    if not os.path.isdir(project_dir):
        copy_tree(
            os.path.join(os.path.abspath(os.path.dirname(__file__)), 'telekeyproject'),
            os.path.join(os.getcwd(), botname)
        )
    else:
        print(f'the {botname} directory is exist!')

def main():
    cli()

if __name__ == "__main__":
    main()
