# coding=utf-8
from typing import Iterable

from .this_package_metadata import package_metadata
from .environment_overlay import EnvironmentOverlay


def _load_run_command():
    from .protected_run_command import run_command

    return run_command


_run_command = package_metadata.extra_features['run_command'].protect(_load_run_command, "Unable to use 'run_command'")


# Re-define run_command the same way to support type hinting for callers
def run_command(
        command=None,
        arguments=None,
        working_directory=None,
        standard_output=None,
        error_output=None,
        show_output=None,
        raise_exceptions=None,
        environment_overlay=None):
    # type: (str, Iterable[str], str, [], [], bool, bool, EnvironmentOverlay) -> int
    return _run_command(
        command,
        arguments,
        working_directory,
        standard_output,
        error_output,
        show_output,
        raise_exceptions,
        environment_overlay)
