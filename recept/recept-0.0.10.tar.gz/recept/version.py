from dataclasses import dataclass


@dataclass
class Version:
    major: int
    minor: int
    build: int

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.build}"


version = Version(0, 0, 10)
__version__ = str(version)
