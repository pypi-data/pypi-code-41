""" an example function and exposing it through __all__ """
from bluemax import context

__all__ = ['add','echo']


def add(int_a: int, int_b: int) -> int:
    """ simple addition of two integers"""
    return int_a + int_b


def echo(what=None):
    """ say again... """
    context.broadcast("echo", what)