import requests
import json
import pandas
from io import StringIO

__all__ = ["JsonWrapper"]

class JsonWrapper(object):
    def __init__(
        self,
        content,
        encoding='utf-8'
    ):
        self.content = content
        self.encoding = encoding
        self.content_text = content.decode(encoding)
    def to_json(self):
        return json.loads(self.content_text.replace("'", '"'))
    def to_pandas(self, *args, **kwargs):
        return pandas.read_csv(
            filepath_or_buffer=StringIO(self.content_text),
            *args,
            **kwargs
        )