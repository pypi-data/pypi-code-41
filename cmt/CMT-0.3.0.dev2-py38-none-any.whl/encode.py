from pathlib import Path

from cmt.a_map import AMap


def encode(source: AMap, file: Path):
    with file.open("wb") as writer:
        writer.write(source.encode())
