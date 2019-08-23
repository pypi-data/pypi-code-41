# coding=utf-8
import logging

from argparse import ArgumentParser
from os import linesep
from sys import exit
from traceback import format_exc
from typing import Any, Generic, Sequence, TypeVar, Union

from .argument_processor import ArgumentProcessor, DEFAULT_LOG_FILE_PATH_ATTRIBUTE, DEFAULT_LOG_LEVEL_ATTRIBUTE
from .command import Command, CommandResult
from ._logging_utilities import setup_logging
from .command_argument_processor import CommandArgumentProcessor


EXIT_CODE_CANCEL_REQUESTED = -10
NamespaceType = TypeVar('NamespaceType')


class CommandLine(Command, Generic[CommandResult]):
    def __init__(
            self,
            argument_parser,
            argument_processor=None,
            log_level_attribute=None,
            log_file_path_attribute=None,
            include_stack_trace_in_unhandled_exceptions=None):
        # type: (ArgumentParser, ArgumentProcessor, str, str) -> None

        if not argument_processor:
            argument_processor = CommandArgumentProcessor()

        if not log_level_attribute:
            log_level_attribute = DEFAULT_LOG_LEVEL_ATTRIBUTE

        if not log_file_path_attribute:
            log_file_path_attribute = DEFAULT_LOG_FILE_PATH_ATTRIBUTE

        if include_stack_trace_in_unhandled_exceptions is None:
            include_stack_trace_in_unhandled_exceptions = True

        self._argument_parser = argument_parser
        self._argument_processor = argument_processor
        self._log_level_attribute = log_level_attribute
        self._log_file_path_attribute = log_file_path_attribute
        self._include_stack_trace_in_unhandled_exceptions = include_stack_trace_in_unhandled_exceptions

    def run(self, arguments=None, namespace=None):
        # type: (Sequence[Any], NamespaceType) -> CommandResult
        parsed_args = self._argument_parser.parse_args(args=arguments, namespace=namespace)

        log_level = self._get_log_level(parsed_args)
        log_file = self._get_log_file(parsed_args)

        setup_logging(log_level=log_level, log_file=log_file)
        from ._core import log

        try:
            return self._argument_processor.process_arguments(parsed_args)
        except SystemExit as exception:
            if exception.code != EXIT_CODE_CANCEL_REQUESTED:
                raise
        except BaseException as exception:
            stack_trace = format_exc()

            if self._include_stack_trace_in_unhandled_exceptions:
                message = "{1}{0}Stack trace: {0}{2}".format(linesep, exception.message, stack_trace)
                log.error(message)
            else:
                log.error(exception.message)
                log.debug("Stack trace: {}{}".format(linesep, format_exc()))
            exit(1)

    def _get_log_level(self, parsed_args):
        # type: (NamespaceType) -> int
        if not hasattr(parsed_args, self._log_level_attribute):
            return logging.INFO

        log_level = getattr(parsed_args, self._log_level_attribute)

        if not isinstance(log_level, str):
            return log_level

        log_level = log_level.upper()
        if not hasattr(logging, log_level):
            raise ValueError("Log level value '{}' does not exist.".format(log_level))

        return getattr(logging, log_level)

    def _get_log_file(self, parsed_args):
        # type: (NamespaceType) -> Union[str, None]
        if not hasattr(parsed_args, self._log_file_path_attribute):
            return None

        return getattr(parsed_args, self._log_file_path_attribute)
