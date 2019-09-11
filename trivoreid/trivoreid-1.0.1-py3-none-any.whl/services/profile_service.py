#!/usr/bin/env python
# coding: utf-8

import requests
import logging

import trivoreid.utils.service_utils as su
from trivoreid.models.profile import Profile
from trivoreid.exceptions import TrivoreIDSDKException, TrivoreIDException

class ProfileService(object):
    '''
    Class to wrap Trivore ID profile API
    '''

    _PROFILE = 'api/rest/v1/user/{}/profile'

    def __init__(self, credentials, oidc_user=None):
        self._server = credentials.server
        self._oidc_user = oidc_user

        if credentials.oidc_client is None:
            self._session = requests
            self._auth = credentials.auth
        else:
            self._session = credentials.oidc_client
            self._auth = None

        self._auth_header = credentials.access_token

    def get(self, userId=None):
        '''Get user's profile.
        Args:
            userId (str) : currently logged in user's unique identifier
        Returns:
            A profile.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        if userId is None:
            userId = self._oidc_user.id

        response = self._session.get(
                        su.uri(self._server, self._PROFILE).format(userId),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 200:
            logging.info('Found profile with user id {}'.format(userId))
            return Profile(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update(self, profile, userId=None):
        '''Update user profile.
        Args:
            userId (str) : user's unique identifier
        Returns:
            Modified user's profile.
        Raises:
            TrivoreIDException if the status code is not 200.
            TrivoreIDSDKException exeption can be raised
        '''

        if 'Profile' not in str(type(profile)):
            raise TrivoreIDSDKException('User type is wrong!')

        if userId is None:
            userId = self._oidc_user.id

        response = self._session.put(
                        su.uri(self._server, self._PROFILE).format(userId),
                        json=profile.serialize(),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 200:
            logging.info('Successfully modified profile with the user id {}'
                                                            .format(userId))
            return Profile(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)
