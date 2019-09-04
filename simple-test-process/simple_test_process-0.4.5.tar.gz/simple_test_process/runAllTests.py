# ------- #
# Imports #
# ------- #

from traceback import format_exc
from .fns import forEach, invoke


# ---- #
# Main #
# ---- #


def runAllTests(stateOrSuite):
    stateOrSuite.before()
    forEach(runTest)(stateOrSuite.tests)
    forEach(runAllTests)(stateOrSuite.suites)
    stateOrSuite.after()


# ------- #
# Helpers #
# ------- #


def runTest(aTest):
    parent = aTest.parentSuite or aTest.rootState
    try:
        forEach(invoke)(parent.beforeEach)
        aTest.before()
        aTest.fn()
        aTest.succeeded = True
    except Exception as e:
        aTest.succeeded = False
        aTest.rootState.succeeded = False
        propagateFailure(aTest.parentSuite)
        aTest.formattedException = format_exc()
        aTest.error = e
    finally:
        aTest.after()
        forEach(invoke)(parent.afterEach)


def propagateFailure(aSuite):
    if aSuite is None:
        return

    if aSuite.succeeded:
        aSuite.succeeded = False
        propagateFailure(aSuite.parentSuite)
