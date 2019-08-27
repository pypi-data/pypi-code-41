# Copyright 2018, 2019 Felix Krull
# Licensed under the MIT license, see LICENSE for details.

from io import TextIOWrapper
from pathlib import Path
from typing import TextIO
from urllib.parse import urlparse
from urllib.request import urlopen


class ConfigSource:
    def __init__(self, stream: TextIO) -> None:
        self.stream = stream

    @property
    def base_dir(self) -> Path:
        raise NotImplementedError

    def has_extension(self, ext: str) -> bool:
        raise NotImplementedError

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stream.close()


class HttpConfigSource(ConfigSource):
    def __init__(self, url: str, path: str) -> None:
        self.path = path
        super().__init__(TextIOWrapper(urlopen(url), encoding='utf-8'))

    def has_extension(self, ext: str) -> bool:
        return self.path.endswith(ext)

    @property
    def base_dir(self) -> Path:
        return Path.cwd()


class FileConfigSource(ConfigSource):
    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(path.open('r', encoding='utf-8'))

    @property
    def base_dir(self) -> Path:
        return self.path.parent

    def has_extension(self, ext: str) -> bool:
        return self.path.name.endswith(ext)


def open(filename_or_url: str) -> ConfigSource:
    parsed_url = urlparse(filename_or_url)
    if parsed_url.scheme in ['http', 'https']:
        return HttpConfigSource(filename_or_url, parsed_url.path)
    else:
        return FileConfigSource(Path(filename_or_url))
