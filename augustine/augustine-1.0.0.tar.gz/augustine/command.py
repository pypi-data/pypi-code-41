# coding=utf-8
from abc import abstractmethod
from typing import Generic, TypeVar


CommandResult = TypeVar('CommandResult')


class Command(Generic[CommandResult], object):
    def __call__(self):
        # type: () -> CommandResult
        return self.run()

    @abstractmethod
    def run(self):
        # type: () -> CommandResult
        pass
