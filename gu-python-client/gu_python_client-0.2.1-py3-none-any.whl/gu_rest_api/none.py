import json


class NoneIt:
    pass

NONE_IT=NoneIt()

def default_none_it(o):
    if isinstance(o, NoneIt):
        return None
    raise TypeError(repr(o) + " is not JSON serializable")


def dumps(o):
    return json.dumps(o, default=default_none_it)

__all__ = ['dumps', 'NONE_IT']

