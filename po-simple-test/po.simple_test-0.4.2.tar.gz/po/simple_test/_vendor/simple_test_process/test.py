from .state import addTest
from .fns import noop


def test(label, *, after=noop, before=noop):
    def wrapper(fn):
        addTest(label, after, before, fn)

    return wrapper
