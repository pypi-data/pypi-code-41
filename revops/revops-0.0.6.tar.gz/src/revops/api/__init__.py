name = "api"

import os
import sys

import requests
import logging

import revops.exceptions

__LOGGING_DEFAULTS__ = {'level': logging.INFO}
__DEFAULT_ENDPOINT__ = 'https://api.revops.io'

logging.basicConfig(**__LOGGING_DEFAULTS__)

class RevOpsAPI(object):
    headers = {}
    """
    This is the RevOps API Client

    Attributes:
        api_key (str): API Key used to access RevOps API Access.
        endpoint (str): API Endpoint to access your RevOps instance.
        If not defined, defaults to 'https://api.revops.io'.
    """
    def __init__(self, api_key = None, endpoint = __DEFAULT_ENDPOINT__):
        self.api_key = os.environ.get('REVOPS_API_KEY', api_key)
        if self.api_key == None or self.api_key == '':
            raise Exception("REVOPS_API_KEY environment variable is not set.")
        self.api_endpoint = os.environ.get('REVOPS_API_ENDPOINT', endpoint)
        self.headers = {
            'X-RevOps-API-Key': self.api_key,
            'Content-Type': 'application/json',
        }

    def __getattr__(self, name):
        resource = __import__(
            "revops.resources.{}".format(name),
            fromlist=["revops.resources"]
        )
        return resource.__api_module__(self)

    def request(self, data, api_resource = None, http_method = "GET"):
        url = "{}/{}".format(self.api_endpoint, api_resource)

        response = requests.request(
            http_method,
            url,
            data=data,
            headers=self.headers,
        )
        if response.status_code == 401:
            raise revops.exceptions.AuthenticationException(
                "Unauthorized key, please check credentials provided.",
                api_resource,
                response,
            )
        return response
