from abc import ABC, abstractmethod
from typing import Dict, Any


class Migration:
    version = None

    def __init__(self, context: Dict[str, Any]) -> None:
        self._version = context.get('version', '')
        self._schema_up = False
        self._schema_down = False

    @property
    def version(self) -> str:
        return self._version

    def schema_up(self) -> None:
        self._schema_up = True

    def schema_down(self) -> None:
        self._schema_down = True
