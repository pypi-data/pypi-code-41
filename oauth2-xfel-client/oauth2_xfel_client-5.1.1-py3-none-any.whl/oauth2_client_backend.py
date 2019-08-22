import logging
import sys
from datetime import datetime

from oauthlib.oauth2 import BackendApplicationClient
from requests import Timeout
from requests_oauthlib.oauth2_session import OAuth2Session

__author__ = 'Luis Maia <luis.maia@xfel.eu>'
__date__ = "September 4, 2014"


class Oauth2ClientBackend(object):
    # Hash that store oauth_token information, including the expiration date
    oauth_token = {}

    # Extra Hash with the headers information necessary to requests calls
    headers = {}

    # Parameter that will store the session used to "invoke" the API's
    session = None

    # Number of retries allowed before deal with the consequences!
    timeout = 3
    max_retries = 3

    def __init__(self, client_id, client_secret, scope, token_url, refresh_url,
                 auth_url, session_token=None):

        # most providers will ask you for extra credentials to be passed along
        # when refreshing tokens, usually for authentication purposes.
        #
        # auto_refresh_kwargs parameter must receive a hash with at least:
        # client_id and client_secret keys
        self.oauth_config = {
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': scope,
            'token_url': token_url,  # '.../oauth/token'
            'refresh_url': refresh_url,  # '.../oauth/token'
            'auth_url': auth_url  # '.../oauth/authorize'
        }

        # Check if Certificate should be checked!
        cert_url = 'https://in.xfel.eu'
        self.ssl_verify = cert_url in self.oauth_config['token_url']

        # Configure client using "Backend Application Flow" Oauth 2.0 strategy
        self.client = BackendApplicationClient(client_id)

        # Negotiate with the server and obtains a valid session_token
        # after this self.session can be used to 'invoke' API's
        self.auth_session(session_token=session_token)

    def auth_session(self, session_token=None):
        # If a session token was passed in & it's still valid,
        # create a session using it.
        if self.is_session_token_dt_valid(session_token):
            self._re_used_existing_session_token(session_token)

        # Otherwise, try to get a new session token.
        else:
            for attempt in range(self.max_retries):
                try:
                    # creates a new session token
                    logging.debug('Will try to create a new session token')
                    self._create_new_session_token()

                except Timeout:
                    # Take care of the timeout exception
                    # Having all attempts failed... we need to deal with it!
                    logging.debug(
                        'Got an exception from the server: {0}'.format(
                            sys.exc_info()[0]))
                    continue
                else:
                    logging.debug('Got a new session token successfully')
                    break

        return True

    def _re_used_existing_session_token(self, session_token):
        self.session = OAuth2Session(
            client_id=self.oauth_config['client_id'],
            client=self.client,
            token=session_token,
            auto_refresh_url=self.oauth_config['refresh_url'],
            auto_refresh_kwargs=self.oauth_config,
            token_updater=self.__token_saver(session_token))

    def _create_new_session_token(self):
        self.session = OAuth2Session(
            client_id=self.oauth_config['client_id'],
            client=self.client)

        session_token = self.session.fetch_token(
            self.oauth_config['token_url'],
            client_id=self.oauth_config['client_id'],
            client_secret=self.oauth_config['client_secret'],
            timeout=self.timeout,
            verify=self.ssl_verify)

        self.__token_saver(session_token)

    def check_session_token(self):
        if not self.is_session_token_valid():
            self.__refresh_session_token()

    def get_session_token(self):
        return self.session.token

    def is_session_token_valid(self):
        current_token = self.get_session_token()
        return Oauth2ClientBackend.is_session_token_dt_valid(current_token)

    #
    # Private helper methods
    #
    def __refresh_session_token(self):
        self.auth_session(session_token=self.get_session_token())

    def __token_saver(self, session_token):
        self.oauth_token['access_token'] = session_token['access_token']
        self.oauth_token['refresh_token'] = None
        self.oauth_token['token_type'] = 'bearer'
        self.oauth_token['expires_at'] = \
            datetime.fromtimestamp(session_token['expires_at'])
        #
        self.headers['Authorization'] = \
            'Bearer ' + session_token['access_token']

    #
    # Static Methods
    #
    @staticmethod
    def is_session_token_dt_valid(session_token, dt=None):
        # Check session_token hash
        if session_token and 'expires_at' in session_token:
            # Convert Unix timestamp (seconds from the epoch) to datetime
            expires_dt = datetime.fromtimestamp(session_token['expires_at'])

            if dt is None:
                dt = datetime.now()

            # return True:
            # 1) If expire datetime is in future (token is still valid)
            # return False:
            # 1) If expire datetime is in past (a new token must be generated)
            return expires_dt > dt

        return False
