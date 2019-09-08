# ------- #
# Imports #
# ------- #

from .internal.getTypedResult import getTypedResult


# ---- #
# Main #
# ---- #


def flattenDeep(collection):
    fnName = flattenDeep.__name__
    typedFlattenDeep = getTypedResult(collection, typeToFlattenDeep, fnName)
    return typedFlattenDeep(collection)


# ------- #
# Helpers #
# ------- #


def flattenDeep_list(aList):
    result = []

    def flattenDeep_recursive(aList):
        for maybeInnerList in aList:
            if isinstance(maybeInnerList, list):
                flattenDeep_recursive(maybeInnerList)
            else:
                result.append(maybeInnerList)

    flattenDeep_recursive(aList)

    return result


typeToFlattenDeep = {list: flattenDeep_list}
