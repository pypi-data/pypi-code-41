from http import HTTPStatus

import requests
from requests_toolbelt.adapters import host_header_ssl


class AuthenticationFailure(Exception):
    """
    An exception wrapping an authentication failure response. If the response
    had a payload, that payload is reported as the exception message, otherwise
    a generic error message is returned.
    """
    GENERIC_ERROR_MESSAGE = (
        'API key is not valid or has expired.'
        ' Please generate a new key in the Catalogue UI and try again.'
    )

    def __init__(self, response=None, message=None):
        self.response = response
        self.message = message

    def __str__(self):
        if self.response and self.response.text:
            return self.response.text
        elif self.message:
            return self.message
        return self.GENERIC_ERROR_MESSAGE


def get_auth_key(api_key, api_root, host=None):
    key = api_key
    auth_header = "Bearer {}".format(key)
    start_session_url = "{}/start-session".format(api_root)

    session = requests.Session()
    headers = {"Authorization": auth_header}

    # if a host has been provided, then we need to set it on the header
    # and activate the certificate check against the header itself
    # rather than the ip address
    if host:
        session.mount('https://', host_header_ssl.HostHeaderSSLAdapter())
        headers["Host"] = host

    r = session.post(start_session_url, headers=headers)
    if r.status_code == HTTPStatus.FORBIDDEN:
        api_key_url = api_root.replace('__api', 'dashboard/my-api-keys')
        error_message = "%s Catalog API Key URL: %s" % (
        AuthenticationFailure.GENERIC_ERROR_MESSAGE, api_key_url)
        raise AuthenticationFailure(message=error_message)
    elif r.status_code != HTTPStatus.OK:
        raise AuthenticationFailure(response=r)

    return r.text
