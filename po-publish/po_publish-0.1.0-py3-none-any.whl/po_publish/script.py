# ------- #
# Imports #
# ------- #

from textwrap import dedent
import is_git_repo_clean
import subprocess
import sys
import toml


# ---- #
# Init #
# ---- #


def printErr(msg):
    print(msg, file=sys.stderr)


# ---- #
# Main #
# ---- #


def main():
    if not is_git_repo_clean.checkSync():
        printErr(
            dedent(
                """
                the git repo is not clean
                aborting publish\
                """
            )
        )
        exit(1)

    with open("pyproject.toml", "r") as f:
        pyproject = toml.load(f)

        githubUrl = pyproject["tool"]["poetry"]["repository"]

    pypiWarning = dedent(
        f"""\
        *Note: This document is best viewed [on github]({githubUrl}).
        Pypi's headers are all caps which presents inaccurate information*
        """
    )
    pypiWarnComment = "<!-- pypiwarn -->"

    with open("./README.md", "r") as f:
        commentedWarn = f.read()

    with open("./README.md", "w") as f:
        f.write(commentedWarn.replace(pypiWarnComment, pypiWarning, 1))

    subprocess.run("poetry publish --build".split(" "))

    with open("README.md", "w") as f:
        f.write(commentedWarn)

    print("donezo!")
