import click

from nicky.managers import SourceManager


@click.command(help='copy nickname source file')
@click.argument('path')
@click.option('--lang', '-l', default='ko', help='language')
def copy(path, lang):
    sm = SourceManager(lang)
    sm.copy(path)
