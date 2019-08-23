# coding=utf-8
from typing import Any, Generic, Type

from .command import Command, CommandResult


class InvokeCommand(Generic[CommandResult], object):
    def __init__(self, command_type):
        # type: (Type[Command]) -> None
        self._command_type = command_type

    def __call__(self, *_, **kwargs):
        # type: (*Any, **Any) -> CommandResult
        # noinspection PyArgumentList
        command = self._command_type(**kwargs)
        return command()
