from abc import ABC, abstractmethod


class AEntity(ABC):
    """
    :ivar type: entity type
    :ivar byte_size: size in bytes the entity uses
    """

    def __init__(self, type_: int, byte_size: int):
        self.type: int = type_
        self.byte_size: int = byte_size

    @classmethod
    @abstractmethod
    def decode(cls, data: bytes, offset: int, debug: bool = False) -> 'AEntity':
        """

        :param data:
        :param offset: without entity type byte
        :param debug:
        """
        raise NotImplementedError

    @abstractmethod
    def encode(self) -> bytearray:
        """
        Includes the entity type.
        """
        raise NotImplementedError
