from typing import List
from abc import ABC, abstractmethod
from ..models import Migration


class Collector(ABC):

    @abstractmethod
    def retrieve(self) -> List[Migration]:
        """Retrieve method to be implemented"""


class MemoryCollector(Collector):
    def __init__(self, migrations: List[Migration]) -> None:
        self.migrations = migrations

    def retrieve(self) -> List[Migration]:
        return self.migrations
