"""Python project helpers."""

import tsh
import click

from recept.apps import rm, find, black, flake8, pydocstyle, pytest


def clean(path: str):
    """Cleanup the project directory from python artifacts.

    Args:
        path: Path to the project directory.
    """
    with tsh.pushd(path):
        # Delete the __pycache__ directories
        r = find(".", "-type", "d", "-name", "__pycache__")
        for path in r.stdout.decode("utf-8").splitlines():
            rm(path)

        # Delete *.py[cod] files if some is left
        r = find(".", "-type", "f", "-name", "*.py[cod]")
        for path in r.stdout.decode("utf-8").splitlines():
            rm(path)

        # Delete jupyter checkpoints
        rm(".ipynb_checkpoints")

        # Remove py.test artifacts
        rm(".pytest_cache")


def shell(namespace=None):
    """Run IPython shell with loaded variables."""
    try:
        from IPython import embed

        user_ns = {}
        if namespace is not None:
            user_ns.update(namespace)
        embed(user_ns=user_ns, colors="neutral")
    except ImportError:
        click.secho("IPython is not installed", fg="red")


def fmt(path: str, target_version: str = "py37", line_length: int = 79):
    """Format the code in path using black.

    Args:
        path: Path to the project dir.
        target_version: Python target version py35, py36, py37...
        line_length: Desired line length.
    """
    black(
        "--safe",
        "--target-version",
        target_version,
        "--line-length",
        str(line_length),
        path,
    )


def check(path: str):
    """Run code checks using flake8 and pydocstyle.

    Args:
        path: Path to the project directory.
    """
    flake8(path)
    pydocstyle(path)


def test(path: str):
    """Run tests using pytest.

    Args:
        path: Path to the project directory.
    """
    pytest("-v", "--cov", path, path)
