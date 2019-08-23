import os
import requests


class Client(object):
    """
    Wrapper for the SoupStars web API.

    >>> from soupstars import Client
    >>> client = Client()
    >>> resp = client.status()
    >>> resp.json['healthy']
    True
    """


    # TODO: generic way of loading config vars
    def __init__(self, token=None):
        self.host = os.environ.get('SOUPSTARS_API_HOST') or 'https://soupstars-cloud.herokuapp.com'
        self.token = token or os.environ.get('SOUPSTARS_API_TOKEN')

    def send(self, path, method='POST', data=None, files=None):
        assert path[0] is '/', f"path must start with `/`, but received {path}"
        url = self.host + path
        headers = {
            'Authorization': self.token
            # TODO: add the version of soupstars, requests, python in use
        }
        resp = requests.request(url=url, method=method, json=data,
                                headers=headers, files=files)
        return resp

    def register(self, email, password):
        data = {
            'email': email,
            'password': password
        }
        return self.send('/register', data=data)

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
