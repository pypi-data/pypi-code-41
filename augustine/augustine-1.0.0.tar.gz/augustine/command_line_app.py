# coding=utf-8
from abc import abstractmethod
from argparse import ArgumentParser
from typing import Any, Generic, Iterable, Mapping

from ._core import log
from .argument_processor import ArgumentProcessor, ProcessorHint
from .command import Command, CommandResult
from .command_argument_processor import CommandArgumentProcessor
from .command_line import CommandLine
from .create_basic_argument_parser import create_basic_argument_parser
from .this_package_metadata import package_metadata


class CommandLineApp(Command, Generic[CommandResult, ProcessorHint]):
    _sub_parsers_attribute = "_{}_sub_processors".format(package_metadata.package_name)

    def __init__(
            self,
            package_name=None,
            package_version=None,
            description=None,
            argument_processor=None,
            log_unhandled_exceptions=None):
        # type: (str, str, str, ArgumentProcessor, bool) -> None
        if log_unhandled_exceptions is None:
            log_unhandled_exceptions = False

        if argument_processor is None:
            argument_processor = CommandArgumentProcessor()

        self._package_name = package_name
        self._package_version = package_version
        self._description = description
        self._argument_processor = argument_processor
        self._log_unhandled_exceptions = log_unhandled_exceptions

    @abstractmethod
    def build_parser(self, parser):
        # type: (ArgumentParser) -> None
        pass

    def add_command(
            self,
            parser,
            name,
            processor_hint,
            help=None,
            defaults=None):
        # type: (ArgumentParser, str, ProcessorHint, str, Mapping[str, Any]) -> ArgumentParser
        if not hasattr(parser, self._sub_parsers_attribute):
            sub_parsers = parser.add_subparsers()
            setattr(parser, self._sub_parsers_attribute, sub_parsers)
        else:
            sub_parsers = getattr(parser, self._sub_parsers_attribute)

        command_parser = sub_parsers.add_parser(name, help=help)

        if not defaults:
            defaults = dict()

        defaults[self._argument_processor.processor_hint_attribute] = processor_hint

        command_parser.set_defaults(**defaults)

        return command_parser

    def set_parser_processor_hint(self, parser, processor_hint):
        # type: (ArgumentParser, Any) -> ArgumentParser
        defaults = dict()
        defaults[self._argument_processor.processor_hint_attribute] = processor_hint
        parser.set_defaults(**defaults)

        log.debug("Successfully set parser processor hint {} with hint name {}".format(
            processor_hint,
            self._argument_processor.processor_hint_attribute))

        return parser

    def main(self, arguments=None):
        # type: (Iterable[Any]) -> CommandResult
        return self.run(arguments)

    def run(self, arguments=None):
        # type: (Iterable[Any]) -> CommandResult
        parser = self._create_parser()
        command_line = CommandLine(
            argument_parser=parser,
            argument_processor=self._argument_processor,
            include_stack_trace_in_unhandled_exceptions=self._log_unhandled_exceptions)
        return command_line()

    def _create_parser(self):
        # type: () -> ArgumentParser
        parser = create_basic_argument_parser(self._package_name, self._package_version, self._description)
        self.build_parser(parser)

        return parser
