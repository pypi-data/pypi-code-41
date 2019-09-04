from .state import addSuite
from .fns import noop


def suite(label, *, after=noop, afterEach=noop, before=noop, beforeEach=noop):
    def wrapper(fn):
        addSuite(label, after, afterEach, before, beforeEach, fn)

    return wrapper
