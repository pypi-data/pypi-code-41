# ------- #
# Imports #
# ------- #

from ...fns import passThrough
from .applyIndentLevels import applyIndentLevels
from .removeSucceededTestsInSuites import removeSucceededTestsInSuites


# ---- #
# Main #
# ---- #


def initRootState(state):
    return passThrough(
        state,
        [
            removeSucceededTestsInSuites,
            applyIndentLevels,
            initializeHasBlankLineAfter,
            initializeParentState,
        ],
    )


# ------- #
# Helpers #
# ------- #


def initializeHasBlankLineAfter(state):
    for suite in state.suites:
        suite.hasBlankLineAfter = False

    return state


def initializeParentState(state):
    for suite in state.suites:
        suite.parentState = state

    for test in state.tests:
        test.parentState = state

    return state
