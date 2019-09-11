#!/usr/bin/env python
# coding: utf-8

import requests
import logging

import trivoreid.utils.service_utils as su
from trivoreid.utils.criteria import Filter
from trivoreid.models.page import Page
from trivoreid.models.accesscontrol import AccessControl
from trivoreid.exceptions import TrivoreIDSDKException, TrivoreIDException

class AccessControlService(object):
    '''
    Class to wrap Trivore ID /accesscontrol API
    '''

    _ACCESS_CONTROLS = 'api/rest/v1/accesscontrol'
    _ACCESS_CONTROL = 'api/rest/v1/accesscontrol/{}'

    def __init__(self, credentials):
        self._server = credentials.server

        if credentials.oidc_client is None:
            self._session = requests
            self._auth = credentials.auth
        else:
            self._session = credentials.oidc_client
            self._auth = None

        self._auth_header = credentials.access_token

    def get_all(self,
                filter_fields=None,
                start_index=0,
                count=100,
                sortBy=None,
                ascending=None):
        '''Get the list of the access controls.
        Args:
            filter_fields (Filter) : utils.Filter class to filter out
                                     the result.
            start_index (int)      : 0-based pagination start index
            count (int)            : pagination page size, max 500,
                                     100 by default
            sortBy (str)           : Sort by attribute name
            ascending (bool)       : Sort direction (ascending or descending)
        Returns:
            Page with the pagination data and the list of access controls.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        params = su.generate_parameters(filter_fields, start_index, count)

        if sortBy != None:
            params['sortBy'] = sortBy

        if ascending != None:
            if ascending:
                params['ascending'] = 'ascending'
            else:
                params['ascending'] = 'descending'

        response = self._session.get(
                                su.uri(self._server, self._ACCESS_CONTROLS),
                                params=params,
                                headers=self._auth_header,
                                auth=self._auth)

        if response.status_code == 200:
            logging.info('Found {} access control objects'.format(
                        len(response.json()['resources'])))

            ls = []
            for l in response.json()['resources']:
                ls.append(AccessControl(l))
            page = Page(response.json(), ls)
            return page
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create(self, accesscontrol):
        '''Create new access control.
        Args:
            accesscontrol (AccessControl) : access control to create.
        Returns:
            New accesscontrol object.
        Raises:
            TrivoreIDSDKException if the type of the AccessControl is wrong
            TrivoreIDException if the status code is not 201.
        '''
        if 'AccessControl' not in str(type(accesscontrol)):
            raise TrivoreIDSDKException('AccessControl type is wrong!')

        response = self._session.post(
                                su.uri(self._server, self._ACCESS_CONTROLS),
                                json=accesscontrol.serialize(),
                                headers=self._auth_header,
                                auth=self._auth)

        if response.status_code == 201:
            accesscontrol = AccessControl(response.json())
            logging.info('Successfully created access control with id {}'
                                                    .format(accesscontrol.id))
            return accesscontrol
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get(self, accesscontrolId):
        '''Get the single access control by id.
        Args:
            accesscontrolId (str) : access control unique identifier
        Returns:
            A access control.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.get(
                        su.uri(self._server, self._ACCESS_CONTROL)
                                                    .format(accesscontrolId),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 200:
            logging.info('Found access control with id {}'.format(accesscontrolId))
            return AccessControl(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update(self, accesscontrol, accesscontrolId=None):
        '''Modify a access control.
        Args:
            accesscontrol (AccessControl) : access control to modify.
            accesscontrolId (str)        : if None, then accesscontrol ID from the
                                          AccessControl object will be used.
        Returns:
            Modified access control object.
        Raises:
            TrivoreIDSDKException if the type of the AccessControl is wrong
            TrivoreIDException if the status code is not 200.
        '''
        if 'AccessControl' not in str(type(accesscontrol)):
            raise TrivoreIDSDKException('AccessControl type is wrong!')

        if accesscontrolId is None:
            accesscontrolId = accesscontrol.id

        response = self._session.put(
                        su.uri(self._server, self._ACCESS_CONTROL)
                                                    .format(accesscontrolId),
                        json=accesscontrol.serialize(),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 200:
            ls = AccessControl(response.json())
            logging.info('Successfully modified access control with the id {}'
                        .format(ls.id))
            return ls
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete(self, accesscontrolId):
        '''Delete access control by id.
        Args:
            accesscontrolId (str) : access control unique identifier
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        response = self._session.delete(
                        su.uri(self._server, self._ACCESS_CONTROL)
                                                .format(accesscontrolId),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 204:
            logging.info('Successfully deleted access control with id {}'
                                                    .format(accesscontrolId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)
