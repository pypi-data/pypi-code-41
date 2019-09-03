from typing import List
import pandas as pd
from openqlab.io.importers import utils
from openqlab.io.base_importer import StreamImporter
from openqlab.io.data_container import DataContainer
import re
from pathlib import Path


class ASCII_Header(StreamImporter):
    NAME = 'ASCII_Header'
    AUTOIMPORTER = False
    STARTING_LINES: List[str] = []
    HEADER_ESCAPE: str = r'[#$%]'
    LINE_SPLIT: str = r'[,:;\s\t]'

    def __init__(self, stream):
        super().__init__(stream)
        self._comment = ''
        self.prefix = f'{Path(self._stream.name).stem}_'

    def read(self):
        self._read_header()

        return DataContainer(
            pd.read_csv(self._stream, sep=None, engine='python', prefix=self.prefix, index_col=0),
            header=self._header)

    def _read_header(self):

        line = True
        while line:
            line = self._stream.readline()
            match = re.match(rf'^{self.HEADER_ESCAPE}{{2}}\s*', line)
            if match:
                self._comment += line[match.end():]
                continue
            match = re.match(rf'^{self.HEADER_ESCAPE}\s*', line)
            if match:
                try:
                    split = re.split(self.LINE_SPLIT, line[match.end():], maxsplit=1)
                    keyword, value = re.split(self.LINE_SPLIT, line[match.end():], maxsplit=1)
                except ValueError:
                    raise utils.UnknownFileType(
                        f"'{self.NAME}' importer: Could not parse header in file '{self._stream.name}'")
                self._header[keyword] = value.strip()
                continue
            if not re.match(r'[-+]*\d+', line):
                pass
            break
        self._header['comment'] = self._comment.strip()
        self._stream.seek(self._stream.tell() - len(line))
