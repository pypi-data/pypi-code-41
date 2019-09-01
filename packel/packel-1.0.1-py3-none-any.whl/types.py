from abc import ABC, abstractmethod
from typing import ClassVar, Type


class PacketType(ABC):
    is_dynamic_length: ClassVar[bool] = False
    type: ClassVar[Type]

    def __get__(self, instance, owner = None):
        # If the class is not initialized, return the descriptor to allow calling static methods.
        if instance is None:
            return self

        return self.value

    def __set__(self, instance, value) -> None:
        if not isinstance(value, self.type):
            raise AttributeError(f"Expected a {self.type}, but was given a {type(value)}.")
        self.value = value

    def __delete__(self, instance):
        self.value = self.default()

    def __init__(self):
        self.value = self.default()

    @staticmethod
    @abstractmethod
    def default():
        pass

    @staticmethod
    @abstractmethod
    def deserialize(b: bytes):
        pass

    @staticmethod
    @abstractmethod
    def serialize(v) -> bytes:
        pass


class Boolean(PacketType):
    is_dynamic_length: ClassVar[bool] = False
    type: ClassVar[Type] = bool

    @staticmethod
    def default() -> bool:
        return False

    @staticmethod
    def deserialize(b: bytes) -> bool:
        return int.from_bytes(b, 'big') == 1

    @staticmethod
    def serialize(v) -> bytes:
        x = 1 if v is True else 0
        return x.to_bytes(1, 'big')


class Bytes(PacketType):
    is_dynamic_length: ClassVar[bool] = True
    type: ClassVar[Type] = bytes

    @staticmethod
    def default() -> bytes:
        return b''

    @staticmethod
    def deserialize(b: bytes) -> bytes:
        return b

    @staticmethod
    def serialize(v) -> bytes:
        return v


class Int32(PacketType):
    is_dynamic_length: ClassVar[bool] = False
    type: ClassVar[Type] = int

    @staticmethod
    def default() -> int:
        return 0

    @staticmethod
    def deserialize(b: bytes) -> int:
        return int.from_bytes(b, 'big')

    @staticmethod
    def serialize(v) -> bytes:
        return v.to_bytes(4, 'big')


class Int64(PacketType):
    is_dynamic_length: ClassVar[bool] = False
    type: ClassVar[Type] = int

    @staticmethod
    def default() -> int:
        return 0

    @staticmethod
    def deserialize(b: bytes) -> int:
        return int.from_bytes(b, 'big')

    @staticmethod
    def serialize(v) -> bytes:
        return v.to_bytes(8, 'big')


class String(PacketType):
    is_dynamic_length: ClassVar[bool] = True
    type: ClassVar[Type] = str

    @staticmethod
    def default() -> str:
        return ''

    @staticmethod
    def deserialize(b: bytes) -> str:
        return b.decode('utf-8')

    @staticmethod
    def serialize(v) -> bytes:
        return v.encode('utf-8')
