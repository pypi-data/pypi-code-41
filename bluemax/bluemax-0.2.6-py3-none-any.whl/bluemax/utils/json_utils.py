"""
    We want to encode datetimes and Decimals to json
"""
import json
from decimal import Decimal
from collections.abc import Callable


class DateTimeEncoder(json.JSONEncoder):
    """
        Encodes datetimes and Decimals
        calls to_json on object if it has that method
    """

    def default(self, obj):  # pylint: disable=W0221,R1710,E0202
        """ return json types """
        if hasattr(obj, "isoformat"):
            return obj.isoformat().replace("T", " ")
        if isinstance(obj, Decimal):
            return float(obj)
        if hasattr(obj, "to_json") and isinstance(getattr(obj, "to_json"), Callable):
            return obj.to_json()


def loads(*args, **kwargs):
    """ calls json.loads """
    return json.loads(*args, **kwargs)


def dumps(obj, **kwargs):
    """ calls json.loads with DateTimeEncoder """
    return json.dumps(obj, cls=DateTimeEncoder, **kwargs)
