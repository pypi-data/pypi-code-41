# ------- #
# Imports #
# ------- #

import re
from .fns import all_, any_, forEach, isEmpty as areEmpty, keepWhen, map_


# ---- #
# Main #
# ---- #

#
# This method mutates state
#


def onlyKeepGreppedTests(state, grepArgs):
    if all_(areEmpty)(grepArgs):
        return state

    grepArgs = map_(allToRegexes)(grepArgs)

    markGreppedTests(state, grepArgs.grepTests)
    markGreppedSuites(state, grepArgs.grepSuites)
    markGreppedTestsAndSuites(state, grepArgs.grep)
    trimNonMarkedTestsAndSuites(state)
    removeAllMarks(state)

    return state


# ------- #
# Helpers #
# ------- #


def mark(testOrSuite):
    testOrSuite._keep = True

    if testOrSuite.parentSuite:
        mark(testOrSuite.parentSuite)


def allToRegexes(grepStrings):
    return map_(lambda aString: re.compile(aString))(grepStrings)


def regexMatches(someString):
    def regexMatches_inner(aRegex):
        return bool(aRegex.search(someString))

    return regexMatches_inner


def markTestIfLabelMatches(regexes):
    def markTestIfLabelMatches_inner(testOrSuite):
        if any_(regexMatches(testOrSuite.label))(regexes):
            mark(testOrSuite)

    return markTestIfLabelMatches_inner


def markGreppedTests(stateOrSuite, grepTests):
    forEach(markTestIfLabelMatches(grepTests))(stateOrSuite.tests)
    forEach(lambda suite: markGreppedTests(suite, grepTests))(
        stateOrSuite.suites
    )


def markAllTestsIfLabelMatches(regexes):
    def markAllTestsIfLabelMatches_inner(suite):
        if any_(regexMatches(suite.label))(regexes):
            forEach(mark)(suite.tests)

    return markAllTestsIfLabelMatches_inner


def markGreppedSuites(stateOrSuite, grepSuites):
    forEach(markAllTestsIfLabelMatches(grepSuites))(stateOrSuite.suites)
    forEach(lambda suite: markGreppedSuites(suite, grepSuites))(
        stateOrSuite.suites
    )


def markGreppedTestsAndSuites(stateOrSuite, grep):
    forEach(markTestIfLabelMatches(grep))(stateOrSuite.tests)
    forEach(markAllTestsIfLabelMatches(grep))(stateOrSuite.suites)
    forEach(lambda suite: markGreppedTestsAndSuites(suite, grep))(
        stateOrSuite.suites
    )


def isMarked(testOrSuite):
    return getattr(testOrSuite, "_keep", False)


def trimNonMarkedTestsAndSuites(stateOrSuite):
    stateOrSuite.tests = keepWhen(isMarked)(stateOrSuite.tests)
    stateOrSuite.suites = keepWhen(isMarked)(stateOrSuite.suites)
    forEach(trimNonMarkedTestsAndSuites)(stateOrSuite.suites)


def removeMark(testOrSuite):
    delattr(testOrSuite, "_keep")


def removeAllMarks(stateOrSuite):
    forEach(removeMark)(stateOrSuite.tests)
    forEach(removeMark)(stateOrSuite.suites)
    forEach(removeAllMarks)(stateOrSuite.suites)
