# -*- coding: utf-8 -*-
"""
    flest.decorators
    ~~~~~~~~~~~~~~~~

    Flest decorator definitions
"""
from decorator import decorate


def get_only(wrapped):
    def wrapper(wrapped, *args, **kwargs):
        return wrapped(*args, **kwargs)

    wrapper = decorate(wrapped, wrapper)
    wrapper.methods = ['GET', 'HEAD']

    return wrapper


def public(wrapped):
    def wrapper(wrapped, *args, **kwargs):
        return wrapped(*args, **kwargs)

    wrapper = decorate(wrapped, wrapper)
    wrapper.allow = ['public']

    return wrapper
