# ------- #
# Imports #
# ------- #

from types import SimpleNamespace
from .internal.getTypedResult import getTypedResult


# ---- #
# Main #
# ---- #


def getListOfCollectionValues(collection):
    fnName = getListOfCollectionValues.__name__
    typedValues = getTypedResult(collection, typeToValues, fnName)
    return typedValues(collection)


# ------- #
# Helpers #
# ------- #


def getListOfCollectionValues_dict(aDict):
    return list(aDict.values())


def getListOfCollectionValues_simpleNamespace(aSimpleNamespace):
    return list(aSimpleNamespace.__dict__.values())


typeToValues = {
    dict: getListOfCollectionValues_dict,
    SimpleNamespace: getListOfCollectionValues_simpleNamespace,
}
