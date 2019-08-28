import os
import json


class JsonStorage:
    def __init__(self):
        self.data = None

    @staticmethod
    def _get_path():
        return os.path.join(
            os.path.expanduser('~'),
            '.config',
            'bmcsf',
            'data.json'
        )

    def _load(self):
        try:
            with open(self._get_path(), 'r') as f:
                self.data = json.load(f)
                return self.data
        except FileNotFoundError:
            self.data = {}
            return self.data

    def _dump(self):
        with open(self._get_path(), 'w') as f:
            json.dump(self.data, f)

    def has(self, key):
        if self.data is None:
            self._load()

        return key in self.data.keys()

    def get(self, key, default_value=None):
        if self.data is None:
            self._load()

        if key not in self.data.keys():
            return default_value

        return self.data[key]

    def set(self, key, value):
        self.data[key] = value
        self._dump()

    def remove(self, key):
        del self.data[key]
        self._dump()
