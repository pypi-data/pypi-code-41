# ------- #
# Imports #
# ------- #

from glob import glob
from os import path
from subprocess import run
from .suite import suite
from .test import test
import importlib.util
import os
import sys

from .fns import (
    discardWhen,
    endsWith,
    forEach,
    joinWith,
    map_,
    passThrough,
    raise_,
    split,
)


# ---- #
# Main #
# ---- #

twoLineSeps = os.linesep + os.linesep


#
# I'm choosing to gather all the tests prior to running any because I feel that
#   will be a simpler design.
#
def gatherTests(aSuite):
    oldCurrentSuite = aSuite.rootState.currentSuite
    aSuite.rootState.currentSuite = aSuite
    aSuite.fn()
    forEach(gatherTests)(aSuite.suites)
    aSuite.rootState.currentSuite = oldCurrentSuite


#
# I can't find a clean way to do this so I'm rolling my own.  The python
#   import system is inherently hacky anyway :(
#
def importTests():
    globStr = path.join("tests", "**", "*.py")

    passThrough(
        globStr,
        [
            recursiveGlob,
            discardWhen(endsWith("__init__.py")),
            map_(toModulePath),
            forEach(importModule),
        ],
    )


def importModule(modulePath):
    try:
        spec = importlib.util.find_spec(modulePath)
        testModule = importlib.util.module_from_spec(spec)
        testModule.test = test
        testModule.suite = suite
        spec.loader.exec_module(testModule)
    except Exception as e:
        raise Exception(f"Error occurred while importing '{modulePath}'") from e


def makeCmd(someStr, beforeOrAfter):
    fname = someStr.strip()
    _base, ext = path.splitext(fname)

    # not sure why this is necessary :(
    relativeFname = path.join(".", fname)

    if ext == ".py":
        return lambda: run([sys.executable, relativeFname])
    elif ext == ".sh":
        return lambda: run([relativeFname])

    raise_(
        ValueError,
        f"""
        incorrect value found in pyproject.toml
          -> tool.simple_test
          -> {beforeOrAfter}

        file extension must be .py or .sh.
        extension found: '{ext}'

        full path to pyproject.toml:
        {path.join(os.getcwd(), "pyproject.toml")}
        """,
    )


def recursiveGlob(globStr):
    return glob(globStr, recursive=True)


def toModulePath(filePathFromTestsDir):
    return passThrough(
        filePathFromTestsDir, [removeExtension, split(os.sep), joinWith(".")]
    )


def removeExtension(filePath):
    return os.path.splitext(filePath)[0]
