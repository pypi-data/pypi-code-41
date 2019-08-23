# coding=utf-8
import sys
from os.path import exists, isfile, join
from sys import executable
from typing import cast, Iterable

from .environment_overlay import EnvironmentOverlay
from ._core import log
from .run_command import run_command


class VirtualEnvPython(object):
    _python_search_paths = [
        join('scripts', 'python.exe'),
        join('scripts', 'python'),
        join('Scripts', 'python.exe'),
        join('Scripts', 'python'),
        join('bin', 'python')]

    def __init__(self, virtualenv_directory=None):
        # type: (str) -> None
        self._virtualenv_directory = virtualenv_directory
        self._python_executable = None

    @property
    def python(self):
        # type: () -> str
        if self._python_executable is None:
            self._python_executable = self._find_python()

        return cast(str, self._python_executable)

    def forget_python(self):
        # type: () -> None
        self._python_executable = None

    def run_package(
            self,
            package,
            arguments=None,
            working_directory=None,
            standard_output=None,
            error_output=None,
            show_output=None,
            raise_exceptions=None,
            environment_overlay=None):
        # type: (str, Iterable[str], str, [], [], bool, bool, EnvironmentOverlay) -> int
        if not self.python:
            raise RuntimeError(
                "Unable to invoke package '{}' with arguments '{}': Cannot find python in virtualenv.".format(
                    package, ' '.join(arguments)))

        run_arguments = [self.python, '-m', package]
        run_arguments += arguments if arguments else list()

        return run_command(
            arguments=run_arguments,
            working_directory=working_directory,
            standard_output=standard_output,
            error_output=error_output,
            show_output=show_output,
            raise_exceptions=raise_exceptions,
            environment_overlay=environment_overlay)

    def _find_python(self):
        # type: () -> str
        if getattr(sys, 'frozen', False) and (not self._virtualenv_directory or not exists(self._virtualenv_directory)):
            raise RuntimeError('Unable to automatically determine interpreter path in frozen Python code.')

        if not self._virtualenv_directory or not exists(self._virtualenv_directory):
            log.debug("No virtualenv directory defined or directory doesn't exist. Using current Python.")
            return executable

        log.debug("Searching for Python in {}...".format(self._virtualenv_directory))

        possible_pythons = [join(self._virtualenv_directory, search_path) for search_path in self._python_search_paths]
        log.debug('Searching for Python in: ' + repr(possible_pythons))

        python = next((possible_python for possible_python in possible_pythons if isfile(possible_python)), None)
        if not python:
            raise RuntimeError("Unable to find Python in {}.".format(self._virtualenv_directory))

        log.debug('Found Python: ' + python)

        return python
