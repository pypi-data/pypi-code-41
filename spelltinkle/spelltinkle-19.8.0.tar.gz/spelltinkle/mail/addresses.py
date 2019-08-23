from pathlib import Path
from typing import Dict, Tuple


class Addresses:
    def __init__(self, path: Path):
        self.path = path
        self.names: Dict[str, Tuple[str, str]]
        self.addresses: Dict[str, str]

    def read(self) -> None:
        self.names = {}
        self.addresses = {}
        if not self.path.is_file():
            return
        for line in self.path.read_text().splitlines():
            addr, short, name = line.split(' ', 2)
            self.names[addr] = (short, name)
            self.addresses[short] = addr

    def short_name(self, addr: str) -> str:
        return self.names.get(addr, (addr, ''))[0]

    def address(self, short_name: str) -> str:
        return self.addresses[short_name]
