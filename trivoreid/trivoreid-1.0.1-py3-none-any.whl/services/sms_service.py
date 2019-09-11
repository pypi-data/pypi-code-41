#!/usr/bin/env python
# coding: utf-8

import requests
import logging

import trivoreid.utils.service_utils as su
from trivoreid.utils.criteria import Filter
from trivoreid.exceptions import TrivoreIDSDKException, TrivoreIDException

class SMSService(object):
    '''
    Class to wrap /sms Trivore ID API.
    '''

    _SEND = 'api/rest/v1/sms/send'
    _REGIONS = 'api/rest/v1/sms/regions'
    _SEND_TO_USER = 'api/rest/v1/user/{}/sms/send'

    def __init__(self, credentials,
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

    def send(self, message):
        '''Send SMS message.
        Args:
            params (SMSMessage)    : SMS message parameters
        Returns:
            Response body
        Raises:
            TrivoreIDException if the status code is not 200.
            TrivoreIDSDKException if the type of the Email is wrong
        '''
        if 'SMSMessage' not in str(type(message)):
            raise TrivoreIDSDKException('SMSMessage type is wrong!')

        response = self._session.post(su.uri(self._server, self._SEND),
                                      json=message.serialize(),
                                headers=self._auth_header,
                                auth=self._auth)

        if response.status_code == 200:
            logging.info('Successfully sent SMS message to a mobile number {}.'
                                .format(message.to))
            return response.json()
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def send_to_user(self, userId, message):
        '''Send SMS message.
        Args:
            userId (str)           : user unique identifier
            message (SMSMessage)   : SMS message parameters
        Returns:
            Response body
        Raises:
            TrivoreIDException if the status code is not 200.
            TrivoreIDSDKException if the type of the Email is wrong
        '''
        if 'SMSMessage' not in str(type(message)):
            raise TrivoreIDSDKException('SMSMessage type is wrong!')

        response = self._session.post(
                    su.uri(self._server, self._SEND_TO_USER).format(userId),
                    json=message.serialize(),
                    headers=self._auth_header,
                    auth=self._auth)

        if response.status_code == 200:
            logging.info('Successfully sent SMS message.')
            return response.json()
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_supported_regions(self):
        '''Get list of all supported regions.
        Returns:
            Regions object
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.get(su.uri(self._server, self._REGIONS),
                                     headers=self._auth_header,
                                     auth=self._auth)

        if response.status_code == 200:
            logging.info('Successfully got the list of regions')
            return response.json()
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def send_to_group_members(self,
                              nsCode,
                              message,
                              *groupIdOrName):
        '''
        Send SMS message to all users belonging to the groups.
        Args:
            nsCode (str)         : namespace code
            message (SMSMessage) : SMS message to send
            groupIdOrName        : group names or ids. Max. 20 groups.
        Returns:
            Rest with responses
        '''
        if len(groupIdOrName) > 20:
            raise TrivoreIDSDKException('Limit of 20 groups was exceeded')

        filt = Filter(Filter.EQUAL, 'name' , groupIdOrName[0])
        for i in range(1, len(groupIdOrName)):
            filt = Filter().or_filters(filt,
                                Filter(Filter.EQUAL, 'name' , groupIdOrName[i]))
            filt = Filter().or_filters(filt,
                                Filter(Filter.EQUAL, 'id' , groupIdOrName[i]))

        groups = self._group_service.get_all(filt)
        groupIDs = []
        for g in groups:
            groupIDs.append(g.id)

        filt2 = Filter(Filter.EQUAL, 'memberOf' , groupIDs[0])

        for i in range(1, len(groupIDs)):
            filt2 = Filter().or_filters(filt2,
                                Filter(Filter.EQUAL, 'memberOf' , groupIDs[i]))

        users = self._user_service.get_all(filt2)

        mobiles_list = []
        for user in users:
            if len(user.mobiles) > 0:
                mobiles_list.append(user.mobiles[0].number)

        responses = []
        for mobile in mobiles_list:
            message.to = mobile
            responses.append(self.send(message))
        return responses
