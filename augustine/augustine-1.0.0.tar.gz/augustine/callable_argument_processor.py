# coding=utf-8
from typing import Any, Callable, Generic, Iterable, Mapping

from .argument_processor import ArgumentProcessor, ProcessArgumentsResult


class CallableArgumentProcessor(ArgumentProcessor, Generic[ProcessArgumentsResult]):
    def __init__(self, ignore_arguments=None):
        # type: (Iterable[str]) -> None
        super(CallableArgumentProcessor, self).__init__(ignore_arguments)

    def process_arguments_with_hint(self, _callable, arguments):
        # type: (Callable[[Mapping[str, Any], ProcessArgumentsResult]], Mapping[str, Any]) -> ProcessArgumentsResult

        return _callable(**arguments)
