from abc import ABC, abstractmethod
from enum import Enum, unique


@unique
class MapType(Enum):
    CMAP = "celaria_map"
    ECMAP = "celaria_edi"

    @staticmethod
    def from_str(text) -> 'MapType':
        if text in [MapType.CMAP.value, MapType.CMAP.name, MapType.CMAP.name.lower()]:
            return MapType.CMAP
        elif text in [MapType.ECMAP.value, MapType.ECMAP.name, MapType.ECMAP.name.lower()]:
            return MapType.ECMAP
        else:
            raise NotImplementedError


class AMap(ABC):
    def __init__(self, identifier: MapType, version: int):
        """
        :vartype identifier: MapType
        :vartype version: int
        """
        self.identifier: MapType = identifier
        self.format_version: int = version

    @classmethod
    @abstractmethod
    def decode(cls, data: bytes, offset: int, debug: bool = False) -> 'AMap':
        raise NotImplementedError

    @abstractmethod
    def encode(self) -> bytearray:
        raise NotImplementedError

    ''' TODO
    @abstractmethod
    def check(self) -> Union[None, str]:
        """
        Returns a string with a message if something weird was found. None if nothing.
        :return:
        """
        raise NotImplementedError
    '''
