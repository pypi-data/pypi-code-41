# coding=utf-8
from os import linesep, pathsep
from typing import Mapping, MutableMapping, Sequence


class EnvironmentOverlay(object):
    def __init__(self, merge=None, overwrite=None, default=None):
        # type: (Mapping[str, Sequence[str]], Mapping[str, Sequence[str]], Mapping[str, Sequence[str]]) -> None
        self._merge = merge if merge else dict()
        self._overwrite = overwrite if overwrite else dict()
        self._default = default if default else dict()

    def overlay(self, environment):
        # type: (Mapping[str, str]) -> Mapping[str, str]
        target = dict(environment)

        self._merge_environment(target)
        self._overwrite_environment(target)
        self._set_environment_defaults(target)

        return target

    def __str__(self):
        # type: () -> str
        return "Merge: {} - Overwrite: {} - Default: {}".format(self._merge, self._overwrite, self._default)

    def __repr__(self):
        # type: () -> str
        return str(
            "{0}\t\tMerge: {0}{1}{0}"
            "\t\tOverwrite: {0}{2}{0}"
            "\t\tDefault: {0}{3}{0}").format(
                linesep,
                self._format_environment(self._merge),
                self._format_environment(self._overwrite),
                self._format_environment(self._default))

    def _merge_environment(self, environment):
        # type: (MutableMapping[str, str]) -> None
        if not self._merge:
            return

        for variable, merge_values in self._merge.items():
            current_value = environment.setdefault(variable, '')
            merge_value = pathsep.join(merge_values)

            if current_value:
                current_value += pathsep

            new_value = current_value + merge_value

            environment[variable] = new_value

    def _overwrite_environment(self, environment):
        # type: (MutableMapping[str, str]) -> None
        if not self._overwrite:
            return

        for variable, overwrite_values in self._overwrite.items():
            overwrite_value = pathsep.join(overwrite_values)
            environment[variable] = overwrite_value

    def _set_environment_defaults(self, environment):
        # type: (MutableMapping[str, str]) -> None
        if not self._default:
            return

        for variable, default_values in self._default.items():
            if variable in environment:
                continue

            default_value = pathsep.join(default_values)
            environment[variable] = default_value

    @staticmethod
    def _format_environment(environment):
        # type: (Mapping[str, str]) -> str
        return linesep.join(["\t\t\t{}={}".format(variable, value) for variable, value in environment.items()])
