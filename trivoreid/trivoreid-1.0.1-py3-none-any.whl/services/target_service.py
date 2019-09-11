#!/usr/bin/env python
# coding: utf-8


import requests
import logging

import trivoreid.utils.service_utils as su
from trivoreid.utils.criteria import Filter
from trivoreid.models.page import Page
from trivoreid.models.target import *
from trivoreid.exceptions import TrivoreIDSDKException, TrivoreIDException

class TargetService(object):
    '''
    Class to wrap Trivore ID /target API
    '''

    _TARGETS = 'api/rest/v1/target'
    _TARGET = 'api/rest/v1/target/{}'

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
                count=100):
        '''Get the list of the targets.
        Args:
            filter_fields (Filter) : utils.Filter class to filter out
                                     the result.
            start_index (int)      : 0-based pagination start index
            count (int)            : pagination page size, max 500,
                                     100 by default
        Returns:
            Page with the pagination data and the list of targets.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        params = su.generate_parameters(filter_fields, start_index, count)

        response = self._session.get(su.uri(self._server, self._TARGETS),
                                params=params,
                                headers=self._auth_header,
                                auth=self._auth)

        if response.status_code == 200:
            logging.info('Found {} targets'.format(
                        len(response.json()['resources'])))

            ls = []
            for l in response.json()['resources']:
                ls.append(Target(l))
            page = Page(response.json(), ls)
            return page
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create(self, target):
        '''Create new target.
        Args:
            target (Target) : target to create.
        Returns:
            New target object.
        Raises:
            TrivoreIDSDKException if the type of the Target is wrong
            TrivoreIDException if the status code is not 201.
        '''
        if 'Target' not in str(type(target)):
            raise TrivoreIDSDKException('Target type is wrong!')

        response = self._session.post(
                                su.uri(self._server, self._TARGETS),
                                json=target.serialize(),
                                headers=self._auth_header,
                                auth=self._auth)

        if response.status_code == 201:
            target = Target(response.json())
            logging.info('Successfully created target with id {}'
                                                    .format(target.id))
            return target
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get(self, targetId):
        '''Get the single target by id.
        Args:
            targetId (str) : target unique identifier
        Returns:
            A target.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.get(
                        su.uri(self._server, self._TARGET).format(targetId),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 200:
            logging.info('Found target with id {}'.format(targetId))
            return Target(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update(self, target, targetId=None):
        '''Modify a target.
        Args:
            target (Target) : target to modify.
            targetId (str)        : if None, then target ID from the
                                          Target object will be used.
        Returns:
            Modified target object.
        Raises:
            TrivoreIDSDKException if the type of the Target is wrong
            TrivoreIDException if the status code is not 200.
        '''
        if 'Target' not in str(type(target)):
            raise TrivoreIDSDKException('Target type is wrong!')

        if targetId is None:
            targetId = target.id

        response = self._session.put(
                        su.uri(self._server, self._TARGET).format(targetId),
                        json=target.serialize(),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 200:
            ls = Target(response.json())
            logging.info('Successfully modified target with the id {}'
                        .format(ls.id))
            return ls
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete(self, targetId):
        '''Delete target by id.
        Args:
            targetId (str) : target unique identifier
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        response = self._session.delete(
                        su.uri(self._server, self._TARGET)
                                                .format(targetId),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 204:
            logging.info('Successfully deleted target with id {}'
                                                    .format(targetId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)
