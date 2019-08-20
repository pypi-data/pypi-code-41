import typing
import struct
import uuid
import datetime
from .rect import Rect


class FileReader:
    def __init__(self, file):
        self.file = file

    def bool(self) -> bool:
        return struct.unpack("?", self.file.read(1))[0]

    def int1(self) -> int:
        return struct.unpack("B", self.file.read(1))[0]

    def uint1(self) -> int:
        return struct.unpack("B", self.file.read(1))[0]

    def int2(self) -> int:
        return struct.unpack("h", self.file.read(2))[0]

    def uint2(self) -> int:
        return struct.unpack("H", self.file.read(2))[0]

    def int4(self) -> int:
        return struct.unpack("i", self.file.read(4))[0]

    def uint4(self) -> int:
        return struct.unpack("I", self.file.read(4))[0]

    def int8(self) -> int:
        return struct.unpack("q", self.file.read(8))[0]

    def uint8(self) -> int:
        return struct.unpack("Q", self.file.read(8))[0]

    def single(self) -> float:
        return struct.unpack("f", self.file.read(4))[0]

    def double(self) -> float:
        return struct.unpack("d", self.file.read(8))[0]

    def bits(self) -> typing.Tuple[bool, bool, bool, bool, bool, bool, bool, bool]:
        data = struct.unpack("B", self.file.read(1))[0]
        return (bool(data & 0b0000_0001),
                bool(data & 0b0000_0010),
                bool(data & 0b0000_0100),
                bool(data & 0b0000_1000),
                bool(data & 0b0001_0000),
                bool(data & 0b0010_0000),
                bool(data & 0b0100_0000),
                bool(data & 0b1000_0000))

    def rect(self) -> Rect:
        left, right, top, bottom = struct.unpack("iiii", self.file.read(16))
        return Rect(left, right, top, bottom)

    def string(self, size=None) -> str:
        if size is None:
            size = self.uint1()
        return str(self.file.read(size), encoding="latin1")

    def uuid(self) -> uuid.UUID:
        # TODO: convert to uuid
        # https://docs.microsoft.com/en-us/dotnet/api/system.guid.tobytearray?view=netframework-4.8
        uuid_bytes = self.file.read(16)
        return uuid_bytes

    def datetime(self) -> datetime.datetime:
        # TODO: convert to datetime
        # https://docs.microsoft.com/it-it/dotnet/api/system.datetime.kind?view=netframework-4.8#System_DateTime_Kind
        datetime_bytes = self.file.read(8)
        return datetime_bytes

    def read_until(self, address: int) -> bytearray:
        data = bytearray()
        while self.file.tell() < address:
            data += self.file.read(1)
        return data

    def skip_until(self, address: int) -> None:
        self.file.seek(address)

    def __repr__(self):
        return f"<FileReader at {hex(self.file.tell())}>"
