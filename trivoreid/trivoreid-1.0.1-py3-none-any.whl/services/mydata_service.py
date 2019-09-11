#!/usr/bin/env python
# coding: utf-8

import requests
import logging

import trivoreid.utils.service_utils as su
from trivoreid.models.mydata import MyDataPackage
from trivoreid.exceptions import TrivoreIDSDKException, TrivoreIDException

class MyDataService(object):

    _MYDATA = 'api/rest/v1/user/{}/mydata'
    _MYDATA_FILE = 'api/rest/v1/user/{}/mydata/{}'
    _USER_MYDATA = 'api/rest/v1/user/{}/mydata/user'

    # not covered
    _DATA_REQUESTS = 'api/rest/v1/user/{}/personaldatarequests'
    _DATA_REQUEST = 'api/rest/v1/user/{}/personaldatarequests/{}'
    _DATA_REQUEST_URI = 'api/rest/v1/user/{}/personaldatarequests/view-uri'

    def __init__(self, credentials):
        self._server = credentials.server

        if credentials.oidc_client is None:
            self._session = requests
            self._auth = credentials.auth
        else:
            self._session = credentials.oidc_client
            self._auth = None

        self._header = credentials.access_token

    def get_package(self, userId=None):
        '''Get package of user MyData entries.
        Args:
            userId (str) : user's ID. If None, then the ID of the OIDC user
                           will be used.
        Returns:
            MyDataPackage object.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        if userId is None:
            userId = self._oidc_client.user.id

        response = self._session.get(
                        su.uri(self._server, self._MYDATA).format(userId),
                        headers=self._header,
                        auth=self._auth)

        if response.status_code == 200:
            logging.info('Found MyData of the user with id {}'.format(userId))
            return MyDataPackage(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def request(self, userId=None):
        '''Request MyData creation for the user.
        Args:
            userId (str) : user's ID. If None, then the ID of the OIDC user
                           will be used.
        Returns:
            MyDataPackage object.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        if userId is None:
            userId = self._oidc_client.user.id

        response = self._session.post(
                        su.uri(self._server, self._MYDATA).format(userId),
                        headers=self._header,
                        auth=self._auth)

        if response.status_code == 200:
            logging.info('Successfully requested MyData creation for the user {}'
                                                            .format(userId))
            return MyDataPackage(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_user_info(self, userId=None):
        '''Get user personal data.
        Args:
            userId (str) : user's ID. If None, then the ID of the OIDC user
                           will be used.
        Returns:
            User personal data.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        if userId is None and self._oidc_client is not None:
            if self._oidc_client.user is not None:
                userId = self._oidc_client.user.id

        uri = su.uri(self._server, self._USER_MYDATA).format(userId)
        response = self._session.get(uri, headers=self._header, auth=self._auth)

        if response.status_code == 200:
            logging.info('Successfully found personal data of the user {}'
                                                            .format(userId))
            return response.json()
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_mydata(self, userId, dataId):
        '''Get a single file from the MyData package.
        Args:
            userId (str) : user id
            dataId (str) : data id
        Returns:
            User personal data.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._MYDATA_FILE).format(userId, dataId)
        response = self._session.get(uri, headers=self._header, auth=self._auth)

        if response.status_code == 200:
            logging.info('Successfully found mydata file () of the user {}'
                                                        .format(dataId, userId))
            return response
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)
