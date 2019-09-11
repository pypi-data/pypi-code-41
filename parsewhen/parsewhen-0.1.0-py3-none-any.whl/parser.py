import datetime
import re
import enum

from . import language
from .language import Language


DATE_BREAK = [
    Language.TIME, Language.DATE, Language.DAY, Language.MONTH,
    Language.YEAR, Language.TIME_12, Language.PREFIX,
]

DUR_BREAK = [
    Language.HOUR, Language.MINUTE, Language.SECOND,
]


class Parsed(enum.Enum):
    
    TIMEDELTA = 0
    DATETIME = 1


def parse(tokens, dates, deltas):
    collection = []
    offset = 0
    start = None
    end = None
    breaking = None

    for index, (kind, value) in enumerate(tokens):
        collection.append((kind, value))

        # Track the last time one of kinds from the break list was seen.
        # Stop tracking if it is a previously parsed kind for this group.
        # This prevents different groups from merging.
        if (breaking is not None and kind in breaking
        and not any(k == kind for k, v in collection[:-1])):
            end = index + 1 - offset

        # If nothing from the breaklist was seen and it was not a word,
        # this means its a different kind of group.
        elif breaking is not None and kind != Language.WORD:
            if start != 0:
                yield from collection[:start - 1]
            yield from _parse_collection(collection[start:end], breaking,
                                         dates, deltas)

            yield from collection[end:-1]

            collection = [(kind, value)]
            offset = index
            start = None
            end = None
            breaking = None
        elif breaking is None and kind == Language.WORD:
            yield (kind, value)

        # Start looking for DATE_BREAK kinds and group them together,
        if breaking is None and kind in DATE_BREAK:
            breaking = DATE_BREAK
            if start is None:
                start = index - offset
                end = start + 1

        # Start looking for DUR_BREAK kinds and group them together,
        if breaking is None and kind in DUR_BREAK:
            breaking = DUR_BREAK
            if start is None:
                start = index - offset
                end = start + 1

    if breaking is not None and collection != []:
        if start != 0:
            yield from collection[:start - 1]
        yield from _parse_collection(collection[start:end], breaking,
                                     dates, deltas)
        yield from collection[end:]


def _parse_collection(collection, breaking, dates, deltas):
    items = strip(collection, Language.WORD)

    if breaking == DATE_BREAK:
        parsers = DATE_PARSERS
        ykind = Parsed.DATETIME
    else:
        parsers = DUR_PARSERS
        ykind = Parsed.TIMEDELTA

    yield (ykind, _parse(items, parsers, dates, deltas))


def strip(tokens, *ignore):
    for (kind, values) in tokens:
        if kind not in ignore:
            yield (kind, values)


def _parse(tokens, parsers, dates, deltas):
    if parsers == DATE_PARSERS:
        result = dates()
    else:
        result = deltas()

    for (kind, values) in tokens:
        parser = parsers.get(kind, None)

        if parser is not None:
            for value in values:
                result = parser(result, value)
    return result


def _parse_time(date, value):
    hr = '0'
    mn = '0'
    sc = '0'

    am = value.endswith('am')
    pm = value.endswith('pm')

    t = value.rstrip('amp')

    if ':' in t:
        hr, mn = t.split(':', 1)
    else:
        hr = int(t)

    if '.' in mn:
        mn, sc = mn.split('.', 1)

    if pm:
        hr = int(hr) + 12
    return date.replace(hour=int(hr), minute=int(mn), second=int(sc))


def _parse_date(date, value):
    day = int(value.rstrip('stndrdth'))
    return date.replace(day=day)


def _parse_day(date, value):
    weekday = language.DAYS.index(value.lower())
    difference = weekday - date.weekday()
    return date.replace(day=date.day + difference)


def _parse_month(date, value):
    month = language.MONTHS.index(value.lower())
    return date.replace(month=month + 1)


def _parse_year(date, value):
    return date.replace(year=int(value))


def _parse_prefix(date, value):
    pref, day = value.split(' ', 1)

    if (pref.lower() in ['next', 'last']
    and day.lower() in language.DAYS + ['week']):
        days = (7 if pref.lower() == 'next' else -7)
        date = date + datetime.timedelta(days=days)

    if day.lower() == 'month':
        months = (1 if pref.lower() == 'next' else -1)
        date = date.replace(month=date.month + months)

    if day.lower() == 'year':
        years = (1 if pref.lower() == 'next' else -1)
        date = date.replace(year=date.year + years)

    elif day.lower() in language.DAYS:
        date = _parse_day(date, day)
    return date


def _parse_hour(duration, value):
    hour = int(value.strip('hours'))
    return duration + duration.__class__(hours=hour)


def _parse_minute(duration, value):
    minute = int(value.strip('minutes'))
    return duration + duration.__class__(minutes=minute)


def _parse_second(duration, value):
    second = int(value.strip('seconds'))
    return duration + duration.__class__(seconds=second)


DATE_PARSERS = {
    Language.TIME: _parse_time,
    Language.TIME_12: _parse_time,
    Language.DATE: _parse_date,
    Language.DAY: _parse_day,
    Language.MONTH: _parse_month,
    Language.YEAR: _parse_year,
    Language.PREFIX: _parse_prefix,
}

DUR_PARSERS = {
    Language.HOUR: _parse_hour,
    Language.MINUTE: _parse_minute,
    Language.SECOND: _parse_second,
}
