from typing import *
from yo_core import *
import gzip
import pickle
import zipfile
import os
from pathlib import Path

class to_text_file(Callable[[Queryable],None]):
    def __init__(self, filename: str, autoflush: bool = False, separator: str ='\n', **kwargs):
        self.filename = filename
        self.autoflush = autoflush
        self.separator = separator
        self.kwargs = kwargs

    def __call__(self, query: Queryable):
        with open(self.filename, 'w', **self.kwargs) as file:
            for item in query:
                file.write(str(item) + self.separator)
                if self.autoflush:
                    file.flush()

class to_zip_text_file(Callable[[Queryable],None]):
    def __init__(self, filename: str, separator: str = '\n'):
        self.filename = filename
        self.separator = separator

    def __call__(self, query):
        with gzip.open(self.filename, 'wb') as f:
            for item in query:
                item += self.separator
                item = bytes(item, 'utf-8')
                f.write(item)


class to_pickle_file(Callable[[Queryable],None]):
    def __init__ (self, filename: str):
        self.filename = filename

    def __call__(self, query):
        with open(self.filename,'wb') as file:
            for item in query:
                dump = pickle.dumps(item)
                length = len(dump)
                length_bytes = length.to_bytes(4,byteorder='big')
                file.write(length_bytes)
                file.write(dump)


class to_zipped_folder(Callable[[Queryable],None]):
    def __init__(self, filename: Union[str,Path], writer: Callable = pickle.dumps, replace=True,compression = zipfile.ZIP_DEFLATED):
        self.filename = filename
        self.compression = compression
        self.writer = writer
        self.replace = replace

    def __call__(self, query):
        if self.replace and os.path.isfile(self.filename):
            os.remove(self.filename)
        with zipfile.ZipFile(self.filename, 'a', compression=self.compression) as zfile:
            for index, item in enumerate(query):
                if not isinstance(item,KeyValuePair):
                    raise ValueError("Items must be KeyValuePairs")
                zfile.writestr(item.key, self.writer(item.value))




