# coding=utf-8
from abc import abstractmethod
from argparse import ArgumentParser
from typing import Type

from .command import Command
from .command_line_app import CommandLineApp


class SimpleCommandLineApp(CommandLineApp):
    def __init__(self, process_arguments_command_type, package_name=None, package_version=None, description=None):
        # type: (Type[Command], str, str, str) -> None
        super(SimpleCommandLineApp, self).__init__(package_name, package_version, description)

        self._process_arguments_command_type = process_arguments_command_type

    @abstractmethod
    def build_simple_parser(self, parser):
        # type: (ArgumentParser) -> ArgumentParser
        pass

    def build_parser(self, parser):
        # type: (ArgumentParser) -> ArgumentParser
        new_parser = self.build_simple_parser(parser)
        if new_parser:
            parser = new_parser

        self.set_parser_processor_hint(parser, self._process_arguments_command_type)

        return parser
