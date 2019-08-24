import requests
from requests.auth import HTTPBasicAuth
from time import time
from .ExceptionsAuth import ExceptionClientSecret


class Auth:
    def __init__(self, client_id, client_secret, sandbox=True):
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__sandbox = sandbox
        self.__token = None
        self.__expires_in = None

        if sandbox is True:
            self.__base_url = 'https://authsandbox.braspag.com.br'
        else:
            self.__base_url = 'https://auth.braspag.com.br'


    """Properties"""
    @property
    def client_id(self):
        return self.__client_id

    @property
    def client_secret(self):
        raise ExceptionClientSecret('ClientSecret is not readble.')

    @property
    def sandbox(self):
        return self.__sandbox

    @property
    def base_url(self):
        return self.__base_url

    @property
    def token(self):
        return self.__token

    @property
    def expires_in(self):
        return self.__expires_in

    """Setters"""
    @client_id.setter
    def client_id(self, client_id: str):
        self.__client_id = client_id

    @client_secret.setter
    def client_secret(self, client_secret: str):
        self.__client_secret = client_secret

    @sandbox.setter
    def sandbox(self, value: bool):
        self.__sandbox = value
        self.__change_ambience()

    def __change_ambience(self):
        if self.sandbox:
            self.__base_url = 'https://authsandbox.braspag.com.br'
        else:
            self.__base_url = 'https://auth.braspag.com.br'

    def generate_token(self):
        auth = HTTPBasicAuth(self.client_id, self.__client_secret)
        body = {'grant_type': 'client_credentials'}
        endpoint = '/oauth2/token'
        response = requests.post(url=self.base_url + endpoint, auth=auth, data=body)
        if response.status_code == 200:
            self.__token = response.json().get('access_token')
            self.__expires_in = time() + response.json().get('expires_in')
            return response.json()
        else:
            return response.status_code

    def expired_token(self):
        if time() >= self.expires_in:
            return True
        else:
            return False
