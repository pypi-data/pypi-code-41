import struct
from typing import Any, Tuple


def debug_print(data: bytes, what: str, value: Any, offset: int = None):
    if offset is None:
        print(f"{to_hex(data)} | ?? - {what} - {value}")
    else:
        print(f"{to_hex(data)} | 0x{hex(offset)[2:].upper()} - {what} - {value}")


def to_hex(data: bytes):
    return ' '.join(["{:02x}".format(x) for x in data]).upper()


def unpack_from(format_: str, buffer: bytes, offset: int, what: Tuple[str, ...], debug: bool):
    """
    Same behaviour as struct.unpack_from.

    :param format_:
    :param buffer:
    :param offset:
    :param what: tuple of message for every unpacked value
    :param debug: use debug mode
    :return:
    """
    unpacked = struct.unpack_from(format_, buffer, offset)
    if debug:
        part_offset = 0
        if format_.startswith("@") or format_.startswith("=") or format_.startswith("<") or format_.startswith(
                ">") or format_.startswith("!"):
            format_ = format_[1:]
        for idx in range(len(unpacked)):
            add_off = struct.calcsize(format_[idx])
            debug_print(buffer[offset + part_offset:offset + part_offset + add_off], what[idx], unpacked[idx],
                        offset + part_offset)
            part_offset += add_off
    return unpacked


class DebugIterUnpack:
    def __init__(self, format_: str, buffer: bytes, what: Tuple[str, ...]):
        """
        Same behaviour as struct.iter_unpack. Does not support the offset.

        :param format_:
        :param buffer:
        :param what: list of tuples of message for every unpacked value
        """
        self.format = format_
        self._iter = struct.iter_unpack(format_, buffer)
        # iterator over the what messages
        self.what = what

    def __iter__(self):
        return self

    def __next__(self):
        unpacked = next(self._iter)
        msg = next(self.what)
        for idx in range(len(unpacked)):
            debug_print(struct.pack(self.format, unpacked[idx]), msg[idx], unpacked[idx])
        return unpacked
