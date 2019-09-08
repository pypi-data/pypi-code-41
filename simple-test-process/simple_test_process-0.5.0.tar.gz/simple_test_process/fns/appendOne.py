# ------- #
# Imports #
# ------- #

from .internal.getTypedResult import getTypedResult


# ---- #
# Main #
# ---- #


def appendOne(el):
    def appendOne_inner(collection):
        typedAppendOne = getTypedResult(
            collection, typeToAppendOne, appendOne.__name__
        )
        return typedAppendOne(el, collection)

    return appendOne_inner


# ------- #
# Helpers #
# ------- #


def appendOne_list(el, aList):
    return aList + [el]


typeToAppendOne = {list: appendOne_list}
