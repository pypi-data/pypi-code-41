import json
from datetime import datetime
import re


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            encoded_object = obj.isoformat()
        else:
            encoded_object = json.JSONEncoder.default(self, obj)
        return encoded_object


def matches_datetime_pattern(str_datetime: str):
    regex = '([0-9]{4})-?(1[0-2]|0[1-9])-?(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):?([0-5][0-9]):([0-5][0-9])\\.([' \
            '0-9]{6})'
    return True if re.match(regex, str_datetime) else False


def object_hook(obj):
    for key in obj.keys():
        value = obj[key]
        if isinstance(value, str) and matches_datetime_pattern(value):
            obj[key] = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')
    return obj


class DateTimeDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=object_hook, *args, **kwargs)
