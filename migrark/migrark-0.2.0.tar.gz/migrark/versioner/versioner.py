from abc import ABC, abstractmethod


class Versioner(ABC):

    @property
    @abstractmethod
    def version(self) -> str:
        """Retrieve method to be implemented"""

    @version.setter
    def version(self, value: str) -> None:
        """Set method to be implemented"""


class MemoryVersioner(Versioner):
    def __init__(self, version: str = '') -> None:
        self.version = version

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, value: str) -> None:
        self._version = value
