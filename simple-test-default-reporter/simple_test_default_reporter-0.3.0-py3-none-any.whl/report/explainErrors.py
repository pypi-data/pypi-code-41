# ------- #
# Imports #
# ------- #

from copy import copy
from ..fns import discardWhen, joinWith, map_, mAppendAllTo, passThrough, reduce
import os


# ---- #
# Init #
# ---- #

border = "-" * 20
twoLineSeps = os.linesep + os.linesep
separator = twoLineSeps + border + twoLineSeps


# ---- #
# Main #
# ---- #


def explainErrors(state):
    rootTestsCopy = passThrough(state.tests, [discardWhen(didSucceed), copy])

    flatTests = passThrough(
        state.suites, [discardWhen(didSucceed), reduce(flattenTests, rootTestsCopy)]
    )

    return passThrough(
        flatTests, [map_(toExplanation), joinWith(separator), wrapInBorder]
    )


# ------- #
# Helpers #
# ------- #


def toExplanation(aTest):
    explanation = []

    if aTest.parentSuite:
        explanation.append("suite: " + aTest.parentSuite.label)

    explanation.append("test: " + aTest.label)
    explanation.append("")

    errorContent = ""
    if "formattedException" in aTest.__dict__:
        errorContent = aTest.formattedException
    else:
        errorContent = str(aTest.error)

    explanation.append(errorContent.strip())
    return os.linesep.join(explanation)


def flattenTests(result, aSuite):
    if hasattr(aSuite, "suites"):
        result = reduce(flattenTests, result)(aSuite.suites)

    return passThrough(aSuite.tests, [discardWhen(didSucceed), mAppendAllTo(result)])


def didSucceed(testOrSuite):
    return testOrSuite.succeeded


def wrapInBorder(content):
    return (
        twoLineSeps + border + twoLineSeps + content + twoLineSeps + border + os.linesep
    )
