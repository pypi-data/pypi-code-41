#!/usr/bin/env python
# coding: utf-8

import requests
import logging

import trivoreid.utils.service_utils as su
from trivoreid.utils.criteria import Filter
from trivoreid.models.groups import Group
from trivoreid.models.page import Page
from trivoreid.exceptions import TrivoreIDSDKException, TrivoreIDException

class GroupService(object):
    '''
    Class to wrap Trivore ID /group API
    '''

    _GROUPS = 'api/rest/v1/group'
    _GROUP = 'api/rest/v1/group/{}'
    _GROUPS_NESTED = 'api/rest/v1/group/{}/nested'

    def __init__(self, credentials):
        self._server = credentials.server

        if credentials.oidc_client is None:
            self._session = requests
            self._auth = credentials.auth
        else:
            self._session = credentials.oidc_client
            self._auth = None

        self._header = credentials.access_token

    def get_all(self,
                filter_fields=None,
                start_index=0,
                count=100):
        '''Get the list of the groups.
        Args:
            filter_fields (Filter) : utils.Filter class to filter out
                                     the result.
            start_index (int)      : 0-based pagination start index
            count (int)            : pagination page size, max 500,
                                     100 by default
        Returns:
            Page with the pagination data and the list of groups.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        params = su.generate_parameters(filter_fields, start_index, count)
        response = self._session.get(su.uri(self._server, self._GROUPS),
                                    params=params,
                                    headers=self._header,
                                    auth=self._auth)

        if response.status_code == 200:
            logging.info('Found {} groups'.format(
                        len(response.json()['resources'])))

            groups = []
            for g in response.json()['resources']:
                groups.append(Group(g))
            page = Page(response.json(), groups)
            return page
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create(self, group):
        '''Create new group.
        Args:
            group (Group) : group to create.
        Returns:
            New group object.
        Raises:
            TrivoreIDSDKException if the type of the Group is wrong
            TrivoreIDException if the status code is not 201.
        '''
        if 'Group' not in str(type(group)):
            raise TrivoreIDSDKException('Group type is wrong!')

        uri = su.uri(self._server, self._GROUPS)
        response = self._session.post(uri,
                                    json=group.serialize(),
                                    headers=self._header,
                                    auth=self._auth)

        if response.status_code == 201:
            group = Group(response.json())
            logging.info('Successfully created group with id {}'.format(
                                group.id))
            return group
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get(self, groupId):
        '''Get the single group by id.
        Args:
            groupId (str) : group unique identifier
        Returns:
            A group.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._GROUP).format(groupId)
        response = self._session.get(uri, headers=self._header, auth=self._auth)

        if response.status_code is 200:
            logging.info('Found group with id {}'.format(groupId))
            return Group(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update(self, group, groupId=None):
        '''Modify a group.
        Args:
            group (Group) : group to modify.
            groupId (str) : if None, then group ID from the Group object will
                            be used.
        Returns:
            Modified group object.
        Raises:
            TrivoreIDSDKException if the type of the Group is wrong
            TrivoreIDException if the status code is not 200.
        '''
        if 'Group' not in str(type(group)):
            raise TrivoreIDSDKException('Group type is wrong!')

        if groupId is None:
            groupId = group.id

        uri = su.uri(self._server, self._GROUP).format(groupId)
        response = self._session.put(uri,
                        json = group.serialize(),
                        headers=self._header,
                        auth=self._auth)

        if response.status_code is 200:
            gr = Group(response.json())
            logging.info('Successfully modified group with the id {}'
                        .format(gr.id))
            return gr
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete(self, groupId):
        '''Delete group by id.
        Args:
            groupId (str) : group unique identifier
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        uri = su.uri(self._server, self._GROUP).format(groupId)
        response = self._session.delete(uri, headers=self._header,
                                             auth=self._auth)

        if response.status_code is 204:
            logging.info('Successfully deleted group with id {}'.format(groupId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_nested_groups(self, groupId):
        '''Get all subgroups of the target group.
        Args:
            groupId (str) : target group unique identifier
        Returns:
            A list of subgroups.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._GROUPS_NESTED).format(groupId)
        response = self._session.get(uri, headers=self._header, auth=self._auth)

        if response.status_code is 200:
            subgroups = []
            for g in response.json():
                subgroups.append(Group(g))
            logging.info('Found subgroups for the group {}'.format(groupId))
            return subgroups
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)
