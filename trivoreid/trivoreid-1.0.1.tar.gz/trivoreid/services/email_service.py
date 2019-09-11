#!/usr/bin/env python
# coding: utf-8

import requests
import logging

import trivoreid.utils.service_utils as su
from trivoreid.utils.criteria import Filter
from trivoreid.exceptions import TrivoreIDSDKException, TrivoreIDException

class EmailService(object):
    '''
    Wrapper for sending email messages through Trivore ID api.
    '''
    _SEND = 'api/rest/v1/email/send'
    _USER_SEND = 'api/rest/v1/user/{}/email/send'
    _GROUP_SEND = 'api/rest/v1/group/{}/email/send'

    def __init__(self,
                 credentials,
                 group_service=None,
                 user_service=None):
        self._group_service = group_service
        self._user_service = user_service
        self._server = credentials.server

        if credentials.oidc_client is None:
            self._session = requests
            self._auth = credentials.auth
        else:
            self._session = credentials.oidc_client
            self._auth = None

        self._auth_header = credentials.access_token

    def send(self, email):
        '''
        Send email message.
        Args:
            email (Email) : email to send
        Raises:
            TrivoreIDException if the status code is not 200.
            TrivoreIDSDKException if the type of the Email is wrong
        '''
        if 'Email' not in str(type(email)):
            raise TrivoreIDSDKException('Email type is wrong!')

        response = self._session.post(su.uri(self._server, self._SEND),
                                      json=email.serialize(),
                                      headers=self._auth_header,
                                      auth=self._auth)

        if response.status_code == 200:
            logging.info('Successfully sent email message.')
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def send_to_user(self, email, userId):
        '''
        Send email message to the user.
        Args:
            email (Email) : email to send
            userId (str)  : user unique identifier
        Raises:
            TrivoreIDSDKException if the type of the Email is wrong
            TrivoreIDException if the status code is not 200.
        '''
        if 'Email' not in str(type(email)):
            raise TrivoreIDSDKException('Email type is wrong!')

        uri = su.uri(self._server, self._USER_SEND).format(userId)
        response = self._session.post(uri,
                                      json=email.serialize(),
                                      headers=self._auth_header,
                                      auth=self._auth)

        if response.status_code == 200:
            logging.info('Successfully sent email message to a user with id {}.'
                                            .format(userId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def send_to_group_members(self, email, groupId):
        '''
        Send email message to all users belonging to the defined groups.
        Args:
            email (Email) : email to send
            groupId (str) : group id.
        '''
        if 'Email' not in str(type(email)):
            raise TrivoreIDSDKException('Email type is wrong!')

        uri = su.uri(self._server, self._GROUP_SEND).format(groupId)
        response = self._session.post(uri,
                                      json=email.serialize(),
                                      headers=self._auth_header,
                                      auth=self._auth)

        if response.status_code == 200:
            logging.info('Successfully sent email message to a group with id {}.'
                                                .format(groupId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)
