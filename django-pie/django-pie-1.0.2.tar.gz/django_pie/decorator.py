# coding: utf-8
from functools import wraps


def test_print(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print('\n######### {}.{}'.format(args[0].__class__.__name__, func.__name__))
        func(*args, **kwargs)
    return wrapper
