import os
import requests

from alfa_sdk.common.helpers import EndpointHelper
from alfa_sdk.common.stores import AuthStore
from alfa_sdk.common.exceptions import (
    CredentialsError,
    TokenNotFoundError,
    AuthenticationError,
)


ALFA_APP_ID = 30


class Authentication:
    user = None
    token = None

    def __init__(self, credentials={}, *, alfa_env):
        endpoint = EndpointHelper(alfa_env=alfa_env)
        url_core = endpoint.resolve("core")
        self._authenticate(url_core, credentials)

    def _authenticate(self, url_core, credentials):
        try:
            token = fetch_token(credentials)
            self.user = validate_token(url_core, token)
            self.token = token
        except:
            client_id, client_secret = fetch_credentials(credentials)
            token = request_oauth_token(url_core, client_id, client_secret)
            self.user = validate_token(url_core, token)
            self.token = token

    def get_token(self):
        if self.token:
            return self.token

        raise TokenNotFoundError()

    def authenticate_request(self, options):
        return authenticate_request(options, self.token)


#


def fetch_token(credentials={}):
    store = AuthStore.get_group()
    cache = AuthStore.get_group("cache")

    if "token" not in credentials:
        if "ALFA_TOKEN" in os.environ:
            credentials["token"] = os.environ.get("ALFA_TOKEN")
        elif "ALFA_ACCESS_TOKEN" in os.environ:
            credentials["token"] = os.environ.get("ALFA_ACCESS_TOKEN")
        elif "ALFA_AUTH0_TOKEN" in os.environ:
            credentials["token"] = os.environ.get("ALFA_AUTH0_TOKEN")
        elif store and "token" in store:
            credentials["token"] = store["token"]
        elif cache and "token" in cache:
            credentials["token"] = cache["token"]

    if "token" not in credentials:
        raise TokenNotFoundError()

    return credentials.get("token")


def fetch_credentials(credentials={}):
    if "client_id" not in credentials:
        store = AuthStore.get_group()

        if "ALFA_CLIENT_ID" in os.environ:
            credentials["client_id"] = os.environ.get("ALFA_CLIENT_ID")
        elif store and "client_id" in store:
            credentials["client_id"] = store["client_id"]

        if "ALFA_CLIENT_SECRET" in os.environ:
            credentials["client_secret"] = os.environ.get("ALFA_CLIENT_SECRET")
        elif store and "client_secret" in store:
            credentials["client_secret"] = store["client_secret"]

    if "client_id" not in credentials or "client_secret" not in credentials:
        raise CredentialsError()

    return credentials.get("client_id"), credentials.get("client_secret")


#


def request_oauth_token(url_core, client_id, client_secret):
    url = url_core + "/api/ApiKeyValidators/requestToken"

    res = requests.post(
        url,
        data={
            "clientId": client_id,
            "clientSecret": client_secret,
            "audience": url_core,
        },
    )
    res = res.json()

    if "error" in res:
        raise AuthenticationError(error=str(res.get("error")))

    token = res["token_type"] + " " + res["access_token"]
    return token


def validate_token(url_core, token):
    if not token:
        raise AuthenticationError(error="No tokens were supplied")

    url = url_core + "/api/ApiKeyValidators/validateTokenForApp"
    options = {"params": {"appId": ALFA_APP_ID}}
    options = authenticate_request(options, token)
    res = requests.get(url, **options)
    res = res.json()

    if "error" in res:
        raise AuthenticationError(error=str(res.get("error")))

    return res


def authenticate_request(options, token):
    if not token:
        raise TokenNotFoundError()

    if "headers" not in options:
        options["headers"] = {}

    options["headers"]["wb-authorization"] = token
    return options

