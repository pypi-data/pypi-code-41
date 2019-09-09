import fire

from functools import wraps


def command(func):
    @wraps(func)
    def wrapper(func):
        fire.Fire(func)

    return wrapper


