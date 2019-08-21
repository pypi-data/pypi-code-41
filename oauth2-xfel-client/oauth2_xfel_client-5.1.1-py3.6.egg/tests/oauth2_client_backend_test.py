"""Oauth2ClientBackend unitary tests"""

import unittest
from datetime import datetime, timedelta

from oauth2_xfel_client.oauth2_client_backend import \
    Oauth2ClientBackend as Oauth2Client
from .common.secrets import *

__author__ = 'Luis Maia <luis.maia@xfel.eu>'
__date__ = "September 4, 2014"


class Oauth2ClientBackendTest(unittest.TestCase):
    def setUp(self):
        self.client_id = CLIENT_OAUTH2_INFO['CLIENT_ID']
        self.client_secret = CLIENT_OAUTH2_INFO['CLIENT_SECRET']
        self.scope = None
        self.auth_url = CLIENT_OAUTH2_INFO['AUTH_URL']
        self.token_url = CLIENT_OAUTH2_INFO['TOKEN_URL']
        self.refresh_url = self.token_url

        self.base_api_url = BASE_API_URL

        self.valid_token = {}
        self.invalid_token = {
            u'access_token': USER_ACCESS_TOKEN,
            u'expires_at': 1410368490.381425,
            u'expires_in': 7200,
            u'token_type': u'bearer'
        }

    @staticmethod
    def validate_token_duration(duration_s, expected=7200):
        """Check that token duration is 2 hours or just under

        Token duration should be 2 hours, but it's sometimes slightly less,
        presumably because of a delay somewhere. Allow up to 5 seconds less.
        """
        assert (expected - 5) <= duration_s <= expected, \
            "Token duration ({}) should be ~= {}".format(duration_s, expected)

    def test_invalid_token_01(self):
        # Passing an invalid_token to the constructor (in param session_token)
        # will create a new token (the same happen when session_token=None)
        oauth_client_invalid = Oauth2Client(self.client_id,
                                            self.client_secret,
                                            self.scope,
                                            self.token_url,
                                            self.refresh_url,
                                            self.auth_url,
                                            session_token=self.invalid_token)

        current_token = oauth_client_invalid.get_session_token()

        ###
        # Checking invalid_token
        ###
        self.assertEqual(
            oauth_client_invalid.is_session_token_dt_valid(self.invalid_token),
            False,
            "Invalid session token expiring date (considering now())")

        ###
        # Checking current_token != invalid_token
        ###
        self.assertNotEqual(self.invalid_token['access_token'],
                            current_token['access_token'],
                            "Invalid token was successfully used")

        self.assertEqual(oauth_client_invalid.oauth_token['access_token'],
                         current_token['access_token'],
                         "oauth_token and current_token must be equal")

        self.assertNotEqual(self.invalid_token['expires_at'],
                            current_token['expires_at'],
                            "Invalid token expires_at was successfully used")
        self.assertEqual(
            oauth_client_invalid.oauth_token['expires_at'],
            datetime.fromtimestamp(current_token['expires_at']),
            "oauth_token and current_token 'expires_at' must be equal")

        self.assertEqual(self.invalid_token['expires_in'],
                         7200,
                         "Token duration is 2 hours (7200 seconds)")

        self.validate_token_duration(current_token['expires_in'])

        self.assertEqual(self.invalid_token['token_type'].lower(),
                         u'bearer',
                         "Token type is 'bearer'")

        self.assertEqual(
            oauth_client_invalid.oauth_token['token_type'].lower(),
            u'bearer',
            "Token type is 'bearer'")

        self.assertEqual(current_token['token_type'].lower(),
                         u'bearer',
                         "Token type is 'bearer'")

        self.assertEqual(oauth_client_invalid.is_session_token_valid(),
                         True,
                         "Invalid session token")

        self.assertEqual(
            oauth_client_invalid.is_session_token_dt_valid(current_token),
            True,
            "Invalid session token expiring date (expect: now)")

        assert not oauth_client_invalid.is_session_token_dt_valid(
            current_token,
            datetime.now() + timedelta(seconds=7205)
        ), "Invalid session token expiring date (expect: 2h:5s in future)"

    def test_invalid_token_override_by_valid_token(self):
        # Passing an invalid_token to the constructor (in param session_token)
        # will create a new token (the same happen when session_token=None)
        oauth_client_invalid = Oauth2Client(self.client_id,
                                            self.client_secret,
                                            self.scope,
                                            self.token_url,
                                            self.refresh_url,
                                            self.auth_url,
                                            session_token=self.invalid_token)

        current_token = oauth_client_invalid.get_session_token()
        self.valid_token = current_token

        # Passing a valid_token should update it's information
        oauth_client_valid = Oauth2Client(self.client_id,
                                          self.client_secret,
                                          self.scope,
                                          self.token_url,
                                          self.refresh_url,
                                          self.auth_url,
                                          session_token=self.valid_token)

        current_token2 = oauth_client_valid.get_session_token()

        ###
        # Checking current_token2 == current_token
        ###
        self.assertEqual(self.valid_token['access_token'],
                         current_token2['access_token'],
                         "Invalid token was successfully used")

        self.assertEqual(oauth_client_invalid.oauth_token['access_token'],
                         current_token2['access_token'],
                         "oauth_token and current_token2 must be equal")

        self.assertEqual(self.valid_token['expires_at'],
                         current_token2['expires_at'],
                         "Invalid token expires_at was successfully used")

        self.assertEqual(
            oauth_client_invalid.oauth_token['expires_at'],
            datetime.fromtimestamp(current_token2['expires_at']),
            "oauth_token and current_token2 'expires_at' must be equal")

        self.validate_token_duration(self.valid_token['expires_in'])
        self.validate_token_duration(current_token2['expires_in'])

        self.assertEqual(self.valid_token['token_type'].lower(),
                         u'bearer',
                         "Token type is 'bearer'")

        self.assertEqual(
            oauth_client_invalid.oauth_token['token_type'].lower(),
            u'bearer',
            "Token type is 'bearer'")

        self.assertEqual(current_token2['token_type'].lower(),
                         u'bearer',
                         "Token type is 'bearer'")

        self.assertEqual(oauth_client_invalid.is_session_token_valid(),
                         True,
                         "Invalid session token")

        self.assertEqual(
            oauth_client_invalid.is_session_token_dt_valid(current_token2),
            True,
            "Invalid session token expiring date (expect: now)")

        assert not oauth_client_invalid.is_session_token_dt_valid(
            current_token2,
            dt=datetime.now() + timedelta(seconds=7205)
        ), "Invalid session token expiring date (expect: 2h:5s in future)"

    def test_invalid_token_03(self):
        # Passing an invalid_token to the constructor (in param session_token)
        # will create a new token (the same happen when session_token=None)
        oauth_client_invalid = Oauth2Client(self.client_id,
                                            self.client_secret,
                                            self.scope,
                                            self.token_url,
                                            self.refresh_url,
                                            self.auth_url,
                                            session_token=self.invalid_token)

        current_token = oauth_client_invalid.get_session_token()
        self.valid_token = current_token

        # Passing a valid_token should update it's information
        oauth_client_valid = Oauth2Client(self.client_id,
                                          self.client_secret,
                                          self.scope,
                                          self.token_url,
                                          self.refresh_url,
                                          self.auth_url,
                                          session_token=self.valid_token)

        current_token3 = oauth_client_valid.get_session_token()

        # check_session_token refreshes the token if it is inactive
        # However, that's not the case in this test
        oauth_client_valid.check_session_token()

        ###
        # Checking current_token3 == current_token
        ###
        self.assertEqual(self.valid_token['access_token'],
                         current_token3['access_token'],
                         "Invalid token was successfully used")

        self.assertEqual(oauth_client_invalid.oauth_token['access_token'],
                         current_token3['access_token'],
                         "oauth_token and current_token3 must be equal")

        self.assertEqual(self.valid_token['expires_at'],
                         current_token3['expires_at'],
                         "Invalid token expires_at was successfully used")

        self.assertEqual(
            oauth_client_invalid.oauth_token['expires_at'],
            datetime.fromtimestamp(current_token3['expires_at']),
            "oauth_token and current_token3 'expires_at' must be equal")

        self.validate_token_duration(self.valid_token['expires_in'])
        self.validate_token_duration(current_token3['expires_in'])

        self.assertEqual(self.valid_token['token_type'].lower(),
                         u'bearer',
                         "Token type is 'bearer'")

        self.assertEqual(
            oauth_client_invalid.oauth_token['token_type'].lower(),
            u'bearer',
            "Token type is 'bearer'")

        self.assertEqual(current_token3['token_type'].lower(),
                         u'bearer',
                         "Token type is 'bearer'")

        self.assertEqual(oauth_client_invalid.is_session_token_valid(),
                         True,
                         "Invalid session token")

        self.assertEqual(
            oauth_client_invalid.is_session_token_dt_valid(current_token3),
            True,
            "Invalid session token expiring date (expect: now)")

        assert not oauth_client_invalid.is_session_token_dt_valid(
            current_token3,
            datetime.now() + timedelta(seconds=7205)
        ), "Invalid session token expiring date (expect: 2h:5s in future)"


if __name__ == '__main__':
    unittest.main()
