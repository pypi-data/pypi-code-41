# coding=utf-8
from typing import Any, Generic, Iterable, TypeVar

from .command import Command
from ._core import log


ResultType = TypeVar('ResultType')


class PrintCommandResults(Generic[ResultType], object):
    def __init__(self, command, use_log_notice=True):
        # type: (Command) -> None
        self._command = command
        self._use_log_info = use_log_notice

    def __call__(self, *args, **kwargs):
        # type: (*Any, **Any) -> ResultType
        log.debug("Command: " + repr(self._command))
        log.debug("Args: " + repr(type(args)))
        log.debug("Kwargs: " + repr(type(kwargs)))
        # noinspection PyArgumentList
        results = self._command(*args, **kwargs)

        self._print_results(results)

        return results

    def _print_results(self, results):
        # type: (Iterable[ResultType]) -> None
        for result in results:
            if self._use_log_info:
                log.notice(result)
            else:
                print(result)
