# coding=utf-8
from abc import abstractmethod
from argparse import Namespace
from typing import Any, Generic, Iterable, Mapping, TypeVar

from ._core import log


ProcessArgumentsResult = TypeVar('ProcessArgumentsResult')
ProcessorHint = TypeVar('ProcessorHint')

DEFAULT_LOG_LEVEL_ATTRIBUTE = 'log_level'
DEFAULT_LOG_FILE_PATH_ATTRIBUTE = 'log_file_path'


class ArgumentProcessor(Generic[ProcessArgumentsResult, ProcessorHint], object):
    processor_hint_attribute = '_processor_hint'

    def __init__(self, ignore_arguments=None):
        # type: (Iterable[str]) -> None
        if ignore_arguments is None:
            ignore_arguments = [DEFAULT_LOG_LEVEL_ATTRIBUTE, DEFAULT_LOG_FILE_PATH_ATTRIBUTE]

        ignore_arguments.append(self.processor_hint_attribute)

        self._ignore_arguments = ignore_arguments

    def process_arguments(self, arguments):
        # type: (Namespace) -> ProcessArgumentsResult
        log.debug('Ignoring arguments: ' + repr(self._ignore_arguments))

        hint = self.get_processor_hint(arguments)

        arguments = vars(arguments)
        for ignore_argument in self._ignore_arguments:
            del arguments[ignore_argument]

        log.debug('Processor arguments: ' + repr(arguments))

        return self.process_arguments_with_hint(hint, arguments)

    @abstractmethod
    def process_arguments_with_hint(self, hint, arguments):
        # type: (ProcessorHint, Mapping[str, Any]) -> ProcessArgumentsResult
        pass

    @property
    def ignore_arguments(self):
        # type: () -> Iterable[str]
        return list(self._ignore_arguments)

    @ignore_arguments.setter
    def ignore_arguments(self, ignore_arguments):
        # type: (Iterable[str]) -> None
        self._ignore_arguments = list(ignore_arguments)

    def get_processor_hint(self, arguments):
        # type: (Namespace) -> ProcessorHint
        if not hasattr(arguments, self.processor_hint_attribute):
            raise RuntimeError('No processor hint provided with the arguments.')

        hint = getattr(arguments, self.processor_hint_attribute)
        log.debug('Processor hint: ' + repr(hint))

        return hint
