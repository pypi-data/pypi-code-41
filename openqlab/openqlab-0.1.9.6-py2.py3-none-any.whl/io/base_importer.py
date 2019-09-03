"""Importer template"""
from abc import ABC, abstractmethod
from inspect import isabstract
import gzip
import io
from typing import Union, List, IO, BinaryIO, TextIO, cast, Tuple, Dict, Optional, Callable, Any, AnyStr
import logging as log
from re import match
from openqlab.io.data_container import DataContainer
from openqlab.io.importers import utils
from pathlib import Path

abstract_class_attribute = property(abstractmethod(lambda *args: None))


class BaseImporter(ABC):
    NAME = cast(str, abstract_class_attribute)
    AUTOIMPORTER = cast(bool, abstract_class_attribute)

    @abstractmethod
    def read(self) -> DataContainer:
        pass

    @classmethod
    def get_subclasses(cls):
        for subclass in cls.__subclasses__():
            yield from subclass.get_subclasses()
            yield subclass

    @classmethod
    def importers(cls) -> Dict[str, 'BaseImporter']:
        importer_dict: dict = {importer.NAME: importer
                               for importer in BaseImporter.get_subclasses()
                               if not isabstract(importer)}
        return importer_dict

    @classmethod
    def auto_importers(cls) -> Dict[str, 'BaseImporter']:
        auto_importers = {name: importer for name, importer in cls.importers().items() if importer.AUTOIMPORTER}
        return auto_importers


class VisaImporter(BaseImporter, ABC):
    pass


class StreamImporter(BaseImporter, ABC):
    """StreamImporter template.

    Incoming streams are not closed.
    """
    STARTING_LINES = cast(Union[List[str], List[bytes]], abstract_class_attribute)
    STARTING_LINES.__doc__ = 'List of strings with a regex to match the first lines.'
    HEADER_MAP: Dict[str, Tuple[Callable, Optional[str]]] = NotImplemented

    ENCODING: str = 'utf8'
    BINARY: bool = False
    HEADER_SPLIT: str = ','

    def __init__(self, data: Union[str, IO, Path]):
        self._header: Dict = {}
        self._opened_file = False
        self._open_stream(data)
        self._header_lines: List = self._check_header()

    def __del__(self):
        if self._opened_file:
            self._stream.close()

    def _open_stream(self, data):
        if isinstance(data, Path):
            data = str(data)
        if isinstance(data, str):
            self._opened_file = True

            # use gzip if it is a gzip file
            opener = gzip.open if data.endswith('.gz') else io.open

            if self.BINARY:
                self._stream = cast(BinaryIO, opener(data, 'rb'))
            else:
                self._stream = cast(TextIO, opener(data, 'rt', encoding=self.ENCODING))
        else:
            self._stream = cast(IO, data)
        self._stream.seek(0)
        log.info(f'importer {self.NAME} should import {self._stream.name}')

    def _check_header(self) -> List:
        lines: List = []  # save the header lines to reuse them if necessary
        log.info(f'starting lines: {self.STARTING_LINES}')
        try:
            for i, start in enumerate(self.STARTING_LINES, 1):
                line = self._stream.readline()
                lines.append(line)
                log.info(f'regex: {start}', f'line: {line}')
                if not isinstance(start, type(line)) or not match(start, line):
                    raise utils.UnknownFileType(
                        f'{self.NAME}: line {i} of file must start with "{start}"')
        except UnicodeDecodeError as e:
            log.info(f'error: {e}')
            raise utils.UnknownFileType(f'{self.NAME}: cannot open file')
        return lines

    def _get_key(self, keyword: str) -> str:
        try:
            key = self.HEADER_MAP[keyword][1]
            if key:
                return key
        except KeyError:
            pass
        return keyword

    def _read_line(self, line: str):
        split = line.strip().split(self.HEADER_SPLIT)
        keyword, *values = split

        if keyword not in self.HEADER_MAP:
            return

        as_type = self.HEADER_MAP[keyword][0]
        keyword = self._get_key(keyword)

        value = values[0]
        self._insert_header_line(keyword, value, as_type)

        if len(values) > 1 and values[1]:
            unit = values[1]
            keyword = self._get_key(keyword + '-unit')
            self._insert_header_line(keyword, unit, str)

    def _insert_header_line(self, key: str,
                            value: str,
                            as_type: Union[type, Callable]):
        if key in self._header:
            return

        if isinstance(as_type, type):
            self._header[key] = as_type(value)
        else:
            as_type = cast(Callable, as_type)
            as_type(key, value)
