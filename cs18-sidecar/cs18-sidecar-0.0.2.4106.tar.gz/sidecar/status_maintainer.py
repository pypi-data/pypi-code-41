
from abc import ABCMeta, abstractmethod
from logging import Logger
from typing import List
from sidecar.sandbox_error import SandboxError


class StatusMaintainer:
    __metaclass__ = ABCMeta

    def __init__(self, logger: Logger):
        self._logger = logger

    @abstractmethod
    def update_lazy_load_artifacts_waiting(self, value: bool):
        raise NotImplementedError

    @abstractmethod
    def update_sandbox_errors(self, errors: List[SandboxError]):
        raise NotImplementedError

    @abstractmethod
    def update_qualiy_status(self, status: str):
        raise NotImplementedError

    @abstractmethod
    def get_sandbox_errors(self) -> List[SandboxError]:
        raise NotImplementedError
