from abc import abstractmethod

from cmt.a_map import AMap, MapType


class ACMap(AMap):
    def __init__(self, version: int):
        super().__init__(MapType.CMAP, version)

    @classmethod
    @abstractmethod
    def decode(cls, data: bytes, offset: int, debug: bool = False) -> 'ACMap':
        raise NotImplementedError

    @abstractmethod
    def encode(self) -> bytearray:
        raise NotImplementedError
