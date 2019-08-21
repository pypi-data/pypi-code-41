# -*- coding: utf-8 -*-
"""DjangoFlow for Google APIs

This Class is use to create workflow for django with Google APIs, for Generating Credentials from Response URL or from Code

Example:
    Generating OAUTH2 Credentials From Code receiving From Javascript (grantOfflineAccess) Code

        $ from django_gauth.utils import DjangoFlow, CLIENT_SECRET_FILE, SCOPES
        $ flow = DjangoFlow.from_client_secrets_file(client_secrets_file=CLIENT_SECRET_FILE, scopes=SCOPES)
        $ creds = flow.get_credentials_from_code(code=code, javascript_callback_url="https://example.org")

    Generating OAUTH2 Credentials from Callback URL

        $ from django_gauth.utils import DjangoFlow, CLIENT_SECRET_FILE, SCOPES
        $ flow = DjangoFlow.from_client_secrets_file(client_secrets_file=CLIENT_SECRET_FILE, scopes=SCOPES)
        $ creds = flow.get_credentails_from_response_url(response_url=request.build_absolute_uri())

    Getting Userinfo From Credentials

        $ userinfo = flow.get_userinfo(creds=creds)

Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

"""

import os
from django.conf import settings
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request

GOOGLE_AUTH_SCOPES = getattr(settings, 'GOOGLE_AUTH_SCOPES', None)
GOOGLE_AUTH_SCOPES.extend([
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
])

SCOPES = list(set(GOOGLE_AUTH_SCOPES))
CLIENT_SECRET_FILE = getattr(settings, "GOOGLE_CLIENT_SECRET_FILE", os.path.join(settings.BASE_DIR, 'credentials.json'))

class DjangoFlow(Flow):

    """ initialize DjangoFlow Class.
            initialize Class just to add Environment Variable just to avoid scopes Errors
                $ os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
    """
    def __init__(self, oauth2session, client_type, client_config, redirect_uri=None, code_verifier=None):
        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
        super().__init__(oauth2session, client_type, client_config,  redirect_uri, code_verifier)

    """ get_auth_url.
        Args:
            request: Django request object
            callback_url: Callback URL where you want to get response
            
    """
    def get_auth_url(self, request, callback_url):
        self.redirect_uri = request.build_absolute_uri(callback_url).replace("http:", "https:")
        auth_url, _ = self.authorization_url(access_type='offline', prompt='consent', include_granted_scopes='true')
        return auth_url

    """get_credentails_from_response_url.
            fetch Token from Response URL
    """
    def get_credentails_from_response_url(self, response_url):
        self.fetch_token(authorization_response=response_url.replace('http:', 'https:'))
        return self.credentials

    """get_credentials_from_code.
        fetch Token from Code
    """
    def get_credentials_from_code(self, code, javascript_callback_url):
        self.redirect_uri = javascript_callback_url.replace('http:', 'https:')
        self.fetch_token(code=code)
        return self.credentials

    """get_userinfo.
        get useringo from credentials
    """
    def get_userinfo(self, creds):
        return id_token.verify_oauth2_token(creds._id_token, Request(), creds._client_id)