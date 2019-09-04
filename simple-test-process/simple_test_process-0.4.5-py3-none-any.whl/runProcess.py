# ------- #
# Imports #
# ------- #

from os import path
from ._vendor.tedent import tedent
from traceback import format_exc
from types import SimpleNamespace as o
from .onlyKeepGreppedTests import onlyKeepGreppedTests
from .runAllTests import runAllTests
from .state import initState
from .utils import gatherTests, importTests, makeCmd, twoLineSeps
from .validateAndGetReportFn import validateAndGetReportFn
import os
from ._vendor import toml
from ._vendor import simple_test_default_reporter

from .fns import forEach, iif, isEmpty, joinWith, map_, noop, passThrough, prependStr


# ---- #
# Main #
# ---- #


def runProcess(*, reporter, silent, grepArgs):
    try:
        silent = silent == "True"
        cliResult = o(stderr=None, stdout=None, code=None)
        after = noop
        before = noop

        if not silent:
            if reporter == "None":
                report = simple_test_default_reporter.report
            else:
                validationResult = validateAndGetReportFn(reporter, silent, cliResult)

                if validationResult.hasError:
                    return validationResult.cliResult

                report = validationResult.report

            reportOpts = None
            if path.isfile("pyproject.toml"):
                allProjectSettings = toml.load("pyproject.toml")
                result = getValueAtPath(allProjectSettings, ["tool", reporter])
                if result.hasValue:
                    reportOpts = result.value

                result = getValueAtPath(allProjectSettings, ["tool", "simple_test"])
                if result.hasValue:
                    if "before" in result.value:
                        before = makeCmd(result.value["before"], "before")

                    if "after" in result.value:
                        after = makeCmd(result.value["after"], "after")

        state = initState()
        state.before = before
        state.after = after
        importTests()

        forEach(gatherTests)(state.suites)
        onlyKeepGreppedTests(state, grepArgs)
        runAllTests(state)

        if not state.testsFound:
            if not silent:
                cliResult.stderr = tedent(
                    f"""
                    No tests were found in any python files under the project's
                    tests directory: '{path.join(os.getcwd(), 'tests')}'

                    Remember you define tests by decorating a function with
                    @test("test label")
                    """
                )

            cliResult.code = 2
            return cliResult

        if isEmpty(state.tests) and isEmpty(state.suites):
            # grepArgs must contain something if this code is reached
            if not silent:
                cliResult.stderr = (
                    "Your grep options failed to match any suites or tests"
                )

            cliResult.code = 2
            return cliResult

        if not silent:
            if reportOpts is None:
                report(state)
            else:
                report(state, reportOpts)

        cliResult.code = iif(state.succeeded, 0, 1)
        return cliResult

    except Exception:
        if not silent:
            cliResult.stderr = (
                os.linesep
                + "An error occurred during simple_test_process"
                + twoLineSeps
                + format_exc()
            )

        cliResult.code = 2
        return cliResult


# ------- #
# Helpers #
# ------- #


def toFormattedGrepArgs(greppedStrings, grepKey):
    return (
        grepKey
        + ":"
        + os.linesep
        + passThrough(greppedStrings, [map_(prependStr("  ")), joinWith(os.linesep)])
    )


def getValueAtPath(aDict, pathToValue):
    result = o(hasValue=None, value=None)
    val = aDict
    for segment in pathToValue:
        if segment not in val:
            result.hasValue = False
            return result

        val = val[segment]

    result.hasValue = True
    result.value = val
    return result
