# ------- #
# Imports #
# ------- #

from .._vendor.po.case_conversion import dashcase
from copy import deepcopy
from os import path
from .._vendor.simple_test_process.parseArgs import _grepArgs
from .validateRunParams import validateRunParams
import os
import sys

from ..fns import (
    flattenDeep,
    getListOfCollectionValues,
    isLaden,
    keepWhen,
    map_,
    passThrough,
    raise_,
)


# ---- #
# Main #
# ---- #


def createRun(subprocessRun):
    return lambda **kwargs: run(subprocessRun, **kwargs)


def run(subprocessRun, *, grepArgs=None, projectDir=None, reporter=None, silent=False):
    if grepArgs is None:
        grepArgs = deepcopy(_grepArgs)

    validateRunParams(grepArgs, projectDir, reporter, silent)

    if projectDir is None:
        projectDir = os.getcwd()
    else:
        projectDir = path.normpath(projectDir)

    if reporter is None:
        reporter = "None"

    ensureTestsDirExists(projectDir)

    cliGrepArgs = toCliGrepArgs(grepArgs)

    subprocessResult = subprocessRun(
        [
            sys.executable,
            "-m",
            "po.simple_test._vendor.simple_test_process",
            reporter,
            str(silent),
            *cliGrepArgs,
        ],
        cwd=projectDir,
    )

    return subprocessResult.returncode


# ------- #
# Helpers #
# ------- #


def ensureTestsDirExists(projectDir):
    testsDir = path.join(projectDir, "tests")
    if not path.isdir(testsDir):
        raise_(
            Exception,
            f"""
            projectDir must contain a directory 'tests'
            projectDir: {projectDir}
            """,
        )


def eachToKeyValuePair(grepVals, grepKey):
    cliGrepKey = f"--{dashcase(grepKey)}"
    return map_(lambda val: [cliGrepKey, val])(grepVals)


def toCliGrepArgs(grepArgs):
    return passThrough(
        grepArgs,
        [
            keepWhen(isLaden),
            map_(eachToKeyValuePair),
            getListOfCollectionValues,
            flattenDeep,
        ],
    )
