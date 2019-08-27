import json
import logging
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
import requests

LIMIT = 500


# Client provides a wrapper around the requests library and provides methods for the Pleio profile API
class Client:
    def __init__(self, base_url, api_secret, read_only=False):
        self.base_url = base_url
        self.api_secret = api_secret
        self.read_only = read_only

        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': 'Bearer {}'.format(self.api_secret)
        })
        self.session.hooks.update({
            'response': lambda r, *args, **kwargs: r.raise_for_status()
        })

        adapter = HTTPAdapter(max_retries=3)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def get_users(self):
        cursor = ""

        while True:
            url = urljoin(self.base_url, 'users?limit={}&cursor={}'.format(LIMIT, cursor))
            data = self.session.get(url).json()

            user = None
            for user in data['users']:
                yield user

            if user:
                cursor = user['guid']
            else:
                break

            if not data['users']:
                break

    def post_user(self, data):
        if self.read_only:
            return False

        url = urljoin(self.base_url, 'users')
        result = self.session.post(url, data=json.dumps(data)).json()
        logging.debug(result)

        return result

    def ban_user(self, guid):
        if self.read_only:
            return False

        url = urljoin(self.base_url, 'users/{}/ban'.format(guid))
        result = self.session.post(url).json()
        logging.debug(result)

        return result

    def unban_user(self, guid):
        if self.read_only:
            return False

        url = urljoin(self.base_url, 'users/{}/unban'.format(guid))
        result = self.session.post(url).json()
        logging.debug(result)

        return result

    def post_avatar(self, guid, avatar):
        if self.read_only:
            return False

        url = urljoin(self.base_url, 'users/{}/avatar'.format(guid))
        result = self.session.post(url, files={
            'avatar': avatar
        }).json()

        logging.debug(result)

        return result

    def post_log(self, data):
        if self.read_only:
            return False

        url = urljoin(self.base_url, 'logs')
        result = self.session.post(url, data=json.dumps(data))
        logging.debug(result)

        return result
