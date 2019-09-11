import datetime

from . import language, lexer, parser


def _date_factory():
    return datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


def _delta_factory():
    return datetime.timedelta(0, 0, 0)


def generate(text, dates=_date_factory, deltas=_delta_factory):
    tokens = language.lex(text)
    yield from parser.parse(language.group(tokens), dates, deltas)


def parse(text, dates=_date_factory, deltas=_delta_factory):
    for (k, v) in generate(text, dates, deltas):
        if k == language.Language.WORD:
            yield ''.join(v)
        else:
            yield v


def replace(text, dates=_date_factory, deltas=_delta_factory):
    return ''.join(map(str, parse(text, dates, deltas)))


def extract(text, ignore=None, dates=_date_factory, deltas=_delta_factory):
    ignore = ignore or [language.Language.WORD]
    yield from (v for (k, v) in generate(text, dates, deltas) if k not in ignore)


def single(text, dates=_date_factory, deltas=_delta_factory, default=None):
    '''Attempts to extract a single datetime or timedelta object.
    If neither is found it will return the default value.
    '''
    items = tuple(extract(text, dates=dates, deltas=deltas))
    if len(items) == 0:
        return default
    return items[0]


def range(start, stop=None, step='24 hours', dates=_date_factory, deltas=_delta_factory):
    '''Iterates through a range of dates yielding a datetime object every
    step. If start is later than stop it will assume step is inverted
    and traverse backwards appropriately.
    '''
    if stop is None:
        end = single(start, default=None, dates=dates, deltas=deltas)
        start = dates()
    else:
        start = single(start, default=None, dates=dates, deltas=deltas)
        end = single(stop, default=None, dates=dates, deltas=deltas)

    step = single(step)

    if start > end:
        check = '__gt__'
        step = -1 * step
    else:
        check = '__lt__'

    while getattr(start, check)(end):
        yield start
        start = start + step

    yield end
