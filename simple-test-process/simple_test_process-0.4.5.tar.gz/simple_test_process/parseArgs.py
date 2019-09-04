# ------- #
# Imports #
# ------- #

from ._vendor.po import case_conversion
from ._vendor.po.case_conversion import camelcase, dashcase
from copy import deepcopy
from types import SimpleNamespace as o

from .fns import (
    getListOfCollectionKeys,
    map_,
    passThrough,
    prependStr,
    raise_,
    toWrittenList,
)


# ---- #
# Init #
# ---- #

#
# case_conversion.dashcase takes more than a single argument so `map_` will pass
#   it the index and original array which may screw things up
#
def dashcase(aString):
    return case_conversion.dashcase(aString)


_grepArgs = o(grep=[], grepSuites=[], grepTests=[])
_grepArgsKeys = passThrough(
    _grepArgs, [getListOfCollectionKeys, map_(dashcase), map_(prependStr("--"))]
)
_availableGrepArgsKeys = toWrittenList(_grepArgsKeys)


# ---- #
# Main #
# ---- #


#
# We can assume the argument order
#   0    reporter
#   1    silent
#   2?+  grep | grepSuites | grepTests
#
#
# and we can also assume
#  - reporter is a non-relative module name
#  - silent is a string boolean
#  - grepArgs may or may not exist.  Validation is only for debugging purposes
#    as calling code should be reliable.
#
#
def parseArgs(*args):
    return o(reporter=args[0], silent=args[1], grepArgs=parseGrepArgs(args[2:]))


# ------- #
# Helpers #
# ------- #


def parseGrepArgs(grepArgs):
    result = deepcopy(_grepArgs)

    i = 0
    grepArgsLen = len(grepArgs)
    while i < grepArgsLen:
        arg = grepArgs[i]
        if arg not in _grepArgsKeys:
            raise_(
                ValueError,
                f"""
                key '{arg}' is invalid
                available grep keys: {_availableGrepArgsKeys}
                """,
            )

        grepKey = arg
        i += 1

        if i == grepArgsLen:
            raise_(
                ValueError,
                f"""
                a value must be given to '{grepKey}'
                """,
            )

        grepVals = getattr(result, camelcase(grepKey))
        grepVals.append(grepArgs[i])
        i += 1

    return result
