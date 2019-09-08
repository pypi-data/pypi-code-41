from .decorators.argIsCallable import argIsCallable


@argIsCallable
def invoke(aCallable):
    return aCallable()
