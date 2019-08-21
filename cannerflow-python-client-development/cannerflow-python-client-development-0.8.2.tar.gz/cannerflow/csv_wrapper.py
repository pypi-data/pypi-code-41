import requests
import csv
import pandas
from io import StringIO

__all__ = ["CsvWrapper"]

class CsvWrapper(object):
    def __init__(
        self,
        content,
        encoding='utf-8'
    ):
        self.content = content
        self.encoding = encoding
        self.content_text = content.decode(self.encoding)
    def to_list(self, delimiter=','):
        cr = csv.reader(self.content_text.splitlines(), delimiter=delimiter)
        return list(cr)

    def to_pandas(self, *args, **kwargs):
        return pandas.read_csv(
            filepath_or_buffer=StringIO(self.content_text),
            *args,
            **kwargs
        )