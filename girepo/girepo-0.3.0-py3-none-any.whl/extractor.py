#!/usr/bin/env python
from datetime import datetime
from collections import OrderedDict


def calculate_star_per(created_at, updated_at, star_count, day_duration=1, round_n=2):
    """

    :param created_at: e.g. 2014-09-18T16:12:01Z
    :param updated_at: e.g. 2014-09-19T16:12:01Z
    :param star_count:
    :param day_duration: if 1, it means per day. if 7, it means per week.
    :param round_n:
    :return:  day_duration * start / (days + 1)
    """
    created_at_tz = created_at.replace('Z', '+00:00')
    updated_at_tz = updated_at.replace('Z', '+00:00')
    delta = datetime.fromisoformat(updated_at_tz) - datetime.fromisoformat(created_at_tz)
    offset_for_zero_division = 1
    return day_duration * round(star_count / (delta.days + offset_for_zero_division), round_n)


def date_format(date_str):
    return date_str.split('T')[0]


def link_format(url):
    return "[link]({0})".format(url)


def fullname_format(owner, name):
    return "{0}/{1}".format(owner, name)


def to_license_name(license_obj):
    return license_obj['name'] if license_obj else "Unknown, see Homepage"


default_mapper = OrderedDict([
    ('fullname', lambda x: fullname_format(
        (x['owner']['login']), x['name'])
     ),
    ('star', lambda x: x['stargazers_count']),
    ('star/day', lambda x: calculate_star_per(
        x['created_at'], x['updated_at'], x['stargazers_count'], day_duration=1)
     ),
    ('created_at', lambda x: date_format(x['created_at'])),
    ('updated_at', lambda x: date_format(x['updated_at'])),
    ('license', lambda x: to_license_name(x['license'])),
    ('language', lambda x: x['language']),
    ('description', lambda x: x['description']),
    ('url', lambda x: link_format(x['html_url'])),
])


def extract(data, mapper):
    return [func(data) for _, func in mapper.items()]
