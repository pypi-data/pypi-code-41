# ------- #
# Imports #
# ------- #

from os import path
from .._vendor.simple_test_process.parseArgs import _grepArgs
from types import SimpleNamespace
from ..fns import all_, isEmpty, isSomething, raise_


# ---- #
# Init #
# ---- #

setOfGrepArgsKeys = set(_grepArgs.__dict__.keys())


# ---- #
# Main #
# ---- #


def validateRunParams(grepArgs, projectDir, reporter, silent):
    if not isinstance(grepArgs, SimpleNamespace):
        raise_(
            TypeError,
            f"""
            'grepArgs' must be an instance of SimpleNamespace
            type: {type(grepArgs).__name__}
            """,
        )

    if not hasAllGrepKeys(grepArgs):
        raise_(
            ValueError,
            f"""
            'grepArgs' must contain all (and only) the available keys
            available keys: {", ".join(_grepArgs.__dict__.keys())}
            keys given: {", ".join(grepArgs.__dict__.keys())}
            """,
        )

    if not all_(areStringLists)(grepArgs):
        raise ValueError("'grepArgs' can only contain lists of strings")

    if isSomething(projectDir):
        if not isinstance(projectDir, str):
            raise_(
                TypeError,
                f"""\
                'projectDir' must be an instance of str
                type: {type(silent).__name__}
                """,
            )

        if isEmpty(projectDir):
            raise ValueError("'projectDir' cannot be an empty string")

        if not path.isabs(projectDir):
            raise_(
                ValueError,
                f"""
                'projectDir' must pass 'os.path.isabs'
                projectDir: {projectDir}
                """,
            )

        if not path.isdir(projectDir):
            raise_(
                ValueError,
                f"""
                'projectDir' must pass 'os.path.isdir'
                projectDir: {projectDir}
                """,
            )

    if isSomething(reporter):
        if not isinstance(reporter, str):
            raise_(
                TypeError,
                f"""
                'reporter' must be an instance of str
                type: {type(reporter).__name__}
                """,
            )

        if isEmpty(reporter):
            raise ValueError("'reporter' cannot be an empty string")

        if reporter.startswith("."):
            raise_(
                ValueError,
                f"""
                relative reporter modules are not yet supported
                reporter: {reporter}
                """,
            )

    if isSomething(silent) and not isinstance(silent, bool):
        raise_(
            TypeError,
            f"""\
            'silent' must be an instance of bool
            type: {type(silent).__name__}
            """,
        )


# ------- #
# Helpers #
# ------- #


def hasAllGrepKeys(grepArgs):
    if len(grepArgs.__dict__) != len(_grepArgs.__dict__):
        return False

    for key in grepArgs.__dict__.keys():
        if key not in setOfGrepArgsKeys:
            return False

    return True


def areStrings(val):
    return isinstance(val, str)


def areStringLists(val):
    return isinstance(val, list) and all_(areStrings)(val)
