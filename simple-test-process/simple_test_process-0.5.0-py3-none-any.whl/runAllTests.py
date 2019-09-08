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

        # I can't think of a good condition for when to attach the stacktrace to
        #   the reporter output.  If we make it opt-in from the expect library
        #   then that forces every error to have metadata that's only meaningful
        #   for simple-test.  Alternatively making it opt-in from simple-test
        #   means every time a library decides they don't want stack trace info
        #   attached we have to update this condition.  So I'm punting for now
        #   in hopes an actual use-case will clarify a solution.
        if type(e).__name__ != "ExpectFailedError":
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
