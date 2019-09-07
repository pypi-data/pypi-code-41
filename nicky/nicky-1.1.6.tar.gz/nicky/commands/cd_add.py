import click

from nicky.managers import SourceManager
from nicky.utils import PREFIX_WORDS, SUFFIX_WORDS


@click.command(help='Add new suffix or Prefix. You can add multiple values with comma separated.')
@click.argument('kind')
@click.argument('values')
@click.option('--lang', '-l', default='ko', help='language')
def add(kind, values, lang):
    sm = SourceManager(lang)
    value_list = values.split(',')

    if kind in PREFIX_WORDS:
        sm.pre_add(value_list)
    elif kind in SUFFIX_WORDS:
        sm.suf_add(value_list)
    else:
        click.BadArgumentUsage('Invalid arguments: {}'.format(kind))
