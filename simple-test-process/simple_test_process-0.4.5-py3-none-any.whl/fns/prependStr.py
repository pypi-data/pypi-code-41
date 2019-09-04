from .decorators.argIsInstance import argIsInstance


@argIsInstance(str)
def prependStr(prependThis):
    fnName = prependStr.__name__

    @argIsInstance(str, fnName)
    def prependStr_inner(toThis):
        return prependThis + toThis

    return prependStr_inner
