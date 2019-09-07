import click

from nicky.base import Nicky


@click.command(help='nickname generating')
@click.argument('count', default=1)
@click.option('--lang', '-l', default='ko', help='language')
def name(count, lang):
    nicky = Nicky(lang)
    nickname = nicky.get_nickname(count)
    print('\n'.join(nickname))
