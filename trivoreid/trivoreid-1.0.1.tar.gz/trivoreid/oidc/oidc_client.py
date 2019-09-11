#!/usr/bin/env python
# coding: utf-8

import requests
import os
import base64

import trivoreid.utils.service_utils as su

from trivoreid.exceptions import TrivoreIDException
from trivoreid.oidc.oidc_user import OIDCUser


class OidcClient(object):
    '''
    Helper to create OIDC client.
    '''

    _OPENID_CONFIG = '.well-known/openid-configuration'
    _ACCESS_TOKEN = 'openid/token'

    def __init__(self,
                 path='/etc/trivoreid/client_sdk.properties',
                 server=None,
                 scopes=None,
                 client_id=None,
                 client_secret=None,
                 username=None,
                 password=None):
        '''
        Initialize OidcClient.
        Args:
            path (str)          : path to properties file.
                                  Default: /etc/trivoreid/client_sdk.properties
            server (str)        : server URL. If None, value from the properties
                                  file will be used.
            scopes (list)       : list of scopes. If None, then all supported
                                  scopes from the openid-configuration will be
                                  used.
            client_id (str)     : client id. If None, then value from the
                                  property file will be used.
            client_secret (str) : client secret. If None, then value from the
                                  property file will be used.
            username (str)      : username. If None, then value from the
                                  property file will be used.
            password (str)      : password. If None, then value from the
                                  property file will be used.

        Example of the properties file for the password grant:

            service.address=<placeholder>
            oidc.client.id=<placeholder>
            oidc.client.secret=<placeholder>
            password.grant.username=<placeholder>
            password.grant.password=<placeholder>

        '''

        properties = su.get_properties(path)

        if server == None:
            self.server = properties.pop('service.address', None)
        else:
            self.server = server
        if client_id == None:
            self._client_id = properties.pop('oidc.client.id', None)
        else:
            self._client_id = client_id
        if client_secret == None:
            self._client_secret = properties.pop('oidc.client.secret', None)
        else:
            self._client_secret = client_secret
        if username == None:
            self._username = properties.pop('password.grant.username', None)
        else:
            self._username = username
        if password == None:
            self._password = properties.pop('password.grant.password', None)
        else:
            self._password = password

        if self.server[-1] != '/':
            self.server += '/'

        response = requests.get(self.server + self._OPENID_CONFIG)

        if response.status_code is 200:
            response = response.json()
            self.issuer = response['issuer']
            self.authorization_endpoint = response['authorization_endpoint']
            self.jwks_uri = response['jwks_uri']
            self.token_endpoint = response['token_endpoint']
            self.userinfo_endpoint = response['userinfo_endpoint']
            self.scopes_supported = response['scopes_supported']
        else:
            raise TrivoreIDException(self._error_response_message(response),
                                     response.status_code)

        if scopes == None:
            self.scopes = self.scopes_supported
        else:
            self.scopes = scopes

        if type(self.scopes) == list:
            self.scopes = ' '.join(self.scopes)

    def get_access_token(self):
        '''
        Get access token using Password Grant Authorization. Client Id, client
        secret, server, username and password should be defined in the
        constructor.
        '''
        authBytes = base64.encodebytes(
                    ('%s:%s' % (self._client_id, self._client_secret)).encode())
        authString = authBytes.decode().replace('\n', '')

        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                  'Authorization': 'Basic ' + authString}

        data = {'grant_type': 'password',
                'username'  : self._username,
                'password'  : self._password,
                'scope'     : self.scopes}

        token_url = self.server + self._ACCESS_TOKEN
        response = requests.post(token_url, params=data, headers=headers)
        if response.status_code is 200:
            txt = ''.join(c for c in response.text if c not in '{}"').split(',')
            tokens = {}
            for t in txt:
                tokens[t.split(':')[0]] = t.split(':')[1]

            access_token = tokens['access_token']
            headers = {'Authorization': 'Bearer ' + access_token}

            response2 = requests.get(self.userinfo_endpoint, headers=headers)
            if response2.status_code is 200:
                self.user = OIDCUser(response2.json())

            return access_token
        else:
            raise TrivoreIDException(self._error_response_message(response),
                                     response.status_code)

    def _error_response_message(self, response):
        try:
            errorMessage = response.json()['errorMessage']
        except:
            errorMessage = 'Unknown error message. Content: {}'.format(response)

        return 'status code {}, {}'.format(response.status_code, errorMessage)
