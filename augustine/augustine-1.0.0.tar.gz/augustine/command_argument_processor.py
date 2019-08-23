# coding=utf-8
from typing import Any, Iterable, Mapping, Type

from .argument_processor import ArgumentProcessor, ProcessArgumentsResult
from .command import Command


class CommandArgumentProcessor(ArgumentProcessor):
    def __init__(self, ignore_arguments=None):
        # type: (Iterable[str]) -> None
        super(CommandArgumentProcessor, self).__init__(ignore_arguments)

    def process_arguments_with_hint(self, command_type, arguments):
        # type: (Type[Command], Mapping[str, Any]) -> ProcessArgumentsResult

        # noinspection PyArgumentList
        command = command_type(**arguments)
        return command()
