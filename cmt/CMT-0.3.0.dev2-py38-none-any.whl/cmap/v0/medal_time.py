from typing import List

from cmt import utils


class MedalTime:
    def __init__(self, platin: int = 0, gold: int = 0, silver: int = 0, bronze: int = 0):
        self.platin: int = platin
        self.gold: int = gold
        self.silver: int = silver
        self.bronze: int = bronze

    def __str__(self):
        return f"platin: {self.platin} | gold: {self.gold} | silver: {self.silver} | bronze: {self.bronze}"


def decode_medal_times(data: bytes, offset: int, debug: bool = False) -> List[MedalTime]:
    """
    Must start with the length byte.

    :param data:
    :param offset:
    :param debug:
    """
    times = utils.unpack_from('<B', data, offset, ("checkpoint times",), debug)[0]
    offset += 1
    m_times = [MedalTime() for _ in range(times)]
    # we do not use iter_unpack because its easier to use the offset debugging
    for i in range(times):
        m_times[i].platin = utils.unpack_from('<I', data, offset, ("platin time",), debug)[0]
        offset += 4

    for i in range(times):
        m_times[i].gold = utils.unpack_from('<I', data, offset, ("gold time",), debug)[0]
        offset += 4

    for i in range(times):
        m_times[i].silver = utils.unpack_from('<I', data, offset, ("silver time",), debug)[0]
        offset += 4

    for i in range(times):
        m_times[i].bronze = utils.unpack_from('<I', data, offset, ("bronze time",), debug)[0]
        offset += 4
    return m_times
