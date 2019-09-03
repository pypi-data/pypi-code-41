import requests
import json
import os
import hmac
from hashlib import sha1


# The following block loads the configurations (such as url) from the config.json file
# ----------------------------------------------------------------------------------------------------------------------

__CURRENT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
__CONFIG_FILE_PATH = os.path.join(__CURRENT_DIRECTORY, 'config.json')

AUTHORIZE_URL = '/general/Authorize'

ILLEGAL_PARAMETERS_EXCEPTION_TEXT = "Illegal parameters passed! Please verify that you're passing the correct" \
                                    " site_token, api_key and api_secret."

with open(__CONFIG_FILE_PATH, 'r') as cfg:
    URL = json.load(cfg)['cfg']['url']

# ----------------------------------------------------------------------------------------------------------------------


class Convizit:
    """
    The class that is used to connect to Convizit DataBase.
    :param site_token: supplied by Convizit
    :param api_key: supplied by Convizit
    :param api_secret: supplied by Convizit
    """
    def __init__(self, site_token, api_key, api_secret):
        self.siteToken = site_token
        self.apiKey = api_key
        self.apiSecret = api_secret
        self.__authorize()

    def __execute_request(self, method, url, data=None, params=None, headers=None):
        if headers is None:
            headers = {}
        if params is None:
            params = {}
        if data is None:
            data = {}
        request_url = URL + url
        if hasattr(self, 'accessToken'):
            headers['X-Auth-Token'] = self.accessToken
        request = requests.request(
            method, request_url, data=data, params=params, headers=headers)
        return request.json()

    def __authorize(self):
        data = {"apiKey": self.apiKey, "siteToken": self.siteToken}
        hash_input = AUTHORIZE_URL + json.dumps(data).replace(' ', '')
        hashed = hmac.new(self.apiSecret.encode('utf-8'), hash_input.encode('utf-8'), sha1)
        hash_result = hashed.hexdigest()
        headers = {'Sign': hash_result}
        response = self.__execute_request('POST', AUTHORIZE_URL, data=data, headers=headers)
        if 'token' in response:
            self.accessToken = response['token']
        else:
            raise ConnectionRefusedError(ILLEGAL_PARAMETERS_EXCEPTION_TEXT)

    def get_events(self, **kwargs):
        """
        Returns projects' events.
        Please refer the documentation to read about available parameters and return fields.
        :param kwargs:
        :return: list of dictionaries
        """
        response = self.__execute_request('GET', '/activity/GetEvents', params=kwargs)
        return response

    def get_sessions(self, **kwargs):
        """
        Returns projects' sessions.
        Please refer the documentation to read about available parameters and return fields.
        :param kwargs:
        :return: list of dictionaries
        """
        response = self.__execute_request('GET', '/activity/GetSessions', params=kwargs)
        return response

    def get_visits(self, **kwargs):
        """
        Returns projects' page visits.
        Please refer the documentation to read about available parameters and return fields.
        :param kwargs:
        :return: list of dictionaries
        """
        response = self.__execute_request('GET', '/activity/GetPageviews', params=kwargs)
        return response

    def get_elements(self, **kwargs):
        """
        Returns projects' elements.
        Please refer the documentation to read about available parameters and return fields.
        :param kwargs:
        :return: list of dictionaries
        """
        response = self.__execute_request('GET', '/activity/GetElements', params=kwargs)
        return response

    def get_pages(self, **kwargs):
        """
        Returns projects' pages.
        Please refer the documentation to read about available parameters and return fields.
        :param kwargs:
        :return: list of dictionaries
        """
        response = self.__execute_request('GET', '/activity/GetPages', params=kwargs)
        return response

