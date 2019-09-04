import requests

from sliceup.functions import *


class SliceUp:
    def __init__(self, host, port='8080'):
        self.host = 'http://' + host + ':' + port + '/'

    def create(self, cmd):
        return self._post_request('create', cmd)

    def summary(self):
        return self._get_request('summary')

    def describe(self, name):
        return self._get_request('describe', {'name': name})

    def insert(self, cmd):
        return self._post_request('insert', cmd)

    def query(self, cmd):
        self._process_args('select', cmd)
        self._process_args('by', cmd)
        self._process_from(cmd)
        result = self._post_request('query', cmd)
        return result.json()

    @staticmethod
    def _process_args(key, cmd):
        if key in cmd:
            selects = cmd[key]
            for i, expr in enumerate(selects):
                if isinstance(expr, str):
                    selects[i] = id(expr)

    @staticmethod
    def _process_from(cmd):
        f = cmd['from']
        if isinstance(f, str):
            cmd['from'] = {'Table': f}

    def _get_request(self, method, payload=None):
        result = requests.get(self.host + method, json=payload)
        return result

    def _post_request(self, method, payload=None):
        result = requests.post(self.host + method, json=payload)
        return result
