from urllib import parse

import requests

import samslacker
from samslacker import version


def build_api_url(url, query):
    scheme, netloc, path, base_query, fragment = parse.urlsplit(url)

    if base_query:
        query = '%s&%s' % (base_query, query)

    return parse.urlunsplit((scheme, netloc, path, query, fragment))


class ApiRequestor(object):
    def __init__(self, token=None, api_base=None, api_version=None):
        self.api_base = api_base or samslacker.api_base
        self.api_version = api_version or samslacker.api_version
        self.token = token or samslacker.token

    def get_api_base(self):
        return '%s/%s' % (self.api_base, self.api_version)

    def get_request_headers(self, token):
        user_agent = 'SamSlacker/%s PythonBindings/%s' % (self.api_version, version.VERSION,)
        headers = {
            'User-Agent': user_agent
        }

        if token is not None:
            headers['Authorization'] = 'Token %s' % (token,)

        if self.api_version is not None:
            headers['SamSlacker-Version'] = self.api_version

        return headers

    def get(self, path):
        return requests.get('%s%s' % (self.get_api_base(), path),
                            headers=self.get_request_headers(self.token))

    def post(self, path, data=None):
        return requests.post('%s%s' % (self.get_api_base(), path),
                             json=data,
                             headers=self.get_request_headers(self.token))

    def put(self, path, data=None):
        return requests.put('%s%s' % (self.get_api_base(), path),
                            json=data,
                            headers=self.get_request_headers(self.token))
