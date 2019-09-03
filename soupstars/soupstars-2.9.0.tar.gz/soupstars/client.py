import os
import requests
import json


class Client(object):
    """
    Wrapper for the SoupStars web API.

    >>> from soupstars import Client
    >>> client = Client()
    >>> resp = client.status()
    >>> resp.json['healthy']
    True
    """

    default_config = {
        'token': None,
        'host': "https://soupstars-cloud.herokuapp.com"
    }

    def __init__(self, config_dir=None, config_file=None, host=None,
                 token=None):
        self.config_file = config_file or "config.json"
        self.config_dir = config_dir or os.environ.get('SOUPSTARS_HOME') \
            or os.path.join(os.path.expanduser('~'), '.soupstars')
        self.config_path = os.path.join(self.config_dir, self.config_file)
        config = self._load_config()
        self.host = host or os.environ.get('SOUPSTARS_HOST') or config['host']
        self.token = token or os.environ.get('SOUPSTARS_TOKEN') or config['token']  # noqa

    def _write_config(self, config=default_config):
        if not os.path.exists(self.config_dir):
            os.mkdir(self.config_dir)
        with open(self.config_path, 'w') as o:
            json.dump(config, o, indent=2)

    def _load_config(self):
        if not os.path.exists(self.config_path):
            self._write_config()
            return self._load_config()
        else:
            with open(self.config_path) as o:
                return json.load(o)

    def update_config(self):
        config = self.config()
        config.pop('path')
        self._write_config(config=config)

    def config(self):
        return {
            'host': self.host,
            'token': self.token,
            'path': self.config_path
        }

    def send(self, path, method='POST', data=None, files=None):
        url = self.host + path
        headers = {'Authorization': self.token}
        resp = requests.request(
            url=url,
            method=method,
            json=data,
            headers=headers,
            files=files
        )
        return resp

    def register(self, email, password):
        data = {
            'email': email,
            'password': password
        }
        return self.send('/register', data=data)

    def login(self, email, password):
        data = {
            'email': email,
            'password': password
        }
        return self.send('/token', data=data)

    def health(self):
        return self.send('/health', method='GET')

    def ls(self):
        return self.send('/list')

    def profile(self):
        return self.send('/profile')

    def push(self, module):
        file_data = open(module, 'rb').read()
        files = {module: file_data}
        return self.send('/push', files=files)

    def pull(self, module):
        data = {'name': module}
        return self.send('/pull', data=data)

    def run(self, module):
        data = {'name': module}
        return self.send('/run', data=data)

    def results(self, module):
        data = {'name': module}
        return self.send('/results', data=data)

    def create_result(self, run_id, parser_id, data, status_code, url, errors):
        return self.send('/results/create', data={
            'result': {
                'run_id': run_id,
                'parser_id': parser_id,
                'data': data,
                'status_code': status_code,
                'url': url,
                'errors': errors
            }
        })
