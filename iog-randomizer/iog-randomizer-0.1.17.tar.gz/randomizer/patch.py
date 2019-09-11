import tempfile
from typing import TypedDict


class PatchStep(TypedDict):
    index: int
    address: int
    data: bytes

    def __init__(self, index: int, address: int, data: bytes):
        self.index = index
        self.address = address
        self.data = data

class Patch:
    step = 0

    def __init__(self, rom_data, logger):
        self.data = dict()
        self.patch_data = []
        self.logger = logger
        self.temp = tempfile.TemporaryFile()
        self.temp.write(rom_data)

    def __del__(self):
        self.temp.close()

    def seek(self, position: int) -> None:
        self.temp.seek(position)

    def write(self, data: bytes) -> None:
        arr = [x for x in data]
        address = int(self.temp.tell())

        self.patch_data.append(PatchStep(self.step, address, arr))
        #  self.data[int(self.temp.tell())] = arr

        self.temp.write(data)
        self.step += 1

    def read(self, n: int = None):
        return self.temp.read(n)

    def find(self, sub, start=None, end=None):
        d = self.read()
        return d.find(sub, start, end)
