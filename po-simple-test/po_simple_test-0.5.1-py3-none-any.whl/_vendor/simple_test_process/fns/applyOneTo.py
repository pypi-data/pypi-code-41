from .decorators.argIsCallable import argIsCallable


@argIsCallable
def applyOneTo(callable):
    def applyOneTo_inner(arg):
        return callable(arg)

    return applyOneTo_inner
