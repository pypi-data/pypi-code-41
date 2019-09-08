# ------- #
# Imports #
# ------- #

from .internal.makeGenericCallFn import makeGenericCallFn
from .internal.getTypedResult import getTypedResult
from .decorators.argIsCallable import argIsCallable


# ---- #
# Main #
# ---- #


@argIsCallable
def any_(predicate):
    fnName = any.__name__
    callPredicate = makeGenericCallFn(predicate, 3, fnName)

    def any_inner(collection):
        typedAny = getTypedResult(collection, typeToAny, fnName)
        return typedAny(callPredicate, collection)

    return any_inner


# ------- #
# Helpers #
# ------- #


def any_list(callPredicate, aList):
    for idx, el in enumerate(aList):
        if callPredicate(el, idx, aList):
            return True

    return False


typeToAny = {list: any_list}
