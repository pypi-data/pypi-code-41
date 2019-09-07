import click

from nicky.managers import SourceManager
from nicky.utils import PREFIX_WORDS, SUFFIX_WORDS


@click.command(help='Sorting suffix or prefix file')
@click.argument('kind', default='')
@click.option('--lang', '-l', default='ko', help='language')
def sort(kind, lang):
    sm = SourceManager(lang)
    if kind in PREFIX_WORDS:
        sm.pre_sorting()
    elif kind in SUFFIX_WORDS:
        sm.suf_ordering()
    elif not kind:
        sm.suf_ordering()
        sm.pre_sorting()
    else:
        click.BadArgumentUsage('Invalid arguments: {}'.format(kind))

