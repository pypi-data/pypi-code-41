import enum
import calendar

from . import lexer


DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
MONTHS = [m.lower() for m in calendar.month_name[1:]]


MODIFIERS = {
    'second': 1,
    'minute': 60,
    'hour': 3600,       # 60 * 60
    'day': 86400,       # 60 * 60 * 24
}

MOD_ALIAS = {
    'sec': MODIFIERS['second'],
    's': MODIFIERS['second'],
    'min': MODIFIERS['minute'],
    'm': MODIFIERS['minute'],
}

MODIFIERS.update(MOD_ALIAS)

PREFIXES = ['next', 'last', 'this']


class Language(enum.Enum):

    WORD = 0
    TIME = 1
    DATE = 2
    DAY = 3
    MONTH = 4
    YEAR = 5
    TIME_12 = 6

    HOUR = 7
    MINUTE = 8
    SECOND = 9
    PREFIX = 10


def lex(text, lexfunc=None):
    '''Lex some text and yield token pairs.
    You can specify a custom starting point for the lexer via the lexer param.
    It assumes lexer is a generator that yields Language enum values.
    '''
    lexfunc = lexfunc or _lex
    lex = lexer.Lexer(text) 

    for kind in lexfunc(lex):
        if lex.start == lex.cursor:
            lex.cursor += 1

        value = lex.slice
        if kind == Language.WORD and value.lower() in DAYS:
            yield (Language.DAY, value)
        elif kind == Language.WORD and value.lower() in MONTHS:
            yield (Language.MONTH, value)
        else:
            yield (kind, value)

        lex.move(0, update=True)

        if lex.eof:
            break


def group(tokens):
    prev = None
    values = []

    for (kind, value) in tokens:
        if prev is None:
            prev = kind

        if kind != prev:
            yield (prev, values)
            prev = None
            values = []

        values.append(value)
        prev = kind

    if len(values):
        yield (prev, values)


def _lex(lex):
    for char in lex.step:

        if lex.slice.lower() in PREFIXES:
            yield from lex_prefix(lex)

        elif char.isnumeric():
            yield from lex_numeric(lex)

        elif not char.isalnum():
            lex.consumewhile(lambda c: c.isalnum())
            yield Language.WORD
            lex.move(-1)

    yield Language.WORD


def lex_prefix(lex):
    possible = DAYS + MONTHS + ['week', 'month', 'year']
    lex.consume(' ', False)
    for pref in possible:
        if lex.next(len(pref)) == pref:
            lex.move(len(pref))
            yield Language.PREFIX
            break
    

def lex_numeric(lex):
    for char in lex.step:

        # Uh oh its actually a date.
        if lex.next(2) in ['st', 'nd', 'th']:
            lex.move(2)
            yield Language.DATE
            break

        if any(m in lex.next(len(m) + 1).strip(' ') for m in MODIFIERS.keys()):
            yield from lex_duration(lex)
        
        # It's a 12 hour time.
        if lex.next(2) in ['am', 'pm']:
            lex.move(2)
            yield Language.TIME_12
            break

        if not char.isnumeric() and char not in [':', '.']:
            break

    # Check if it was a 24 hour time or a year,
    length = abs(lex.cursor - lex.start)
    if length == 4 and lex.slice.isnumeric():
       yield Language.YEAR
    elif ':' in lex.slice:
        # 24 hour time
        yield Language.TIME

    # Backup required.
    lex.move(-1)


def lex_duration(lex):
    char = lex.char
    if char == ' ':
        lex.move(1)

    for m in sorted(MODIFIERS.keys(), key=len, reverse=True):
        if (len(m) == 1 and m == lex.next(1)
        or len(m) != 1 and m == lex.next(len(m))):
            lex.move(len(m))

            if lex.next(1) == 's':
                lex.move(1)

            if MODIFIERS[m] == MODIFIERS['second']:
                yield Language.SECOND
            elif MODIFIERS[m] == MODIFIERS['minute']:
                yield Language.MINUTE
            elif MODIFIERS[m] == MODIFIERS['hour']:
                yield Language.HOUR
