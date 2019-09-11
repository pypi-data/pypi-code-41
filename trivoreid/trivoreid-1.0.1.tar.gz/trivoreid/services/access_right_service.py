#!/usr/bin/env python
# coding: utf-8

import requests
import logging

import trivoreid.utils.service_utils as su
from trivoreid.utils.criteria import Filter
from trivoreid.models.page import Page
from trivoreid.models.access_right import Permission, BuiltInRole, CustomRole
from trivoreid.exceptions import TrivoreIDSDKException, TrivoreIDException

class AccessRightService(object):
    '''
    Class to wrap Trivore ID /role API
    '''

    _PERMISSIONS = 'api/rest/v1/permission'
    _PERMISSION = 'api/rest/v1/permission/{}'
    _BUILTIN_ROLES = 'api/rest/v1/role/builtin'
    _CUSTOM_ROLES = 'api/rest/v1/role/custom'
    _CUSTOM_ROLE = 'api/rest/v1/role/custom/{}'

    def __init__(self, credentials):
        self._server = credentials.server

        if credentials.oidc_client is None:
            self._session = requests
            self._auth = credentials.auth
        else:
            self._session = credentials.oidc_client
            self._auth = None

        self._header = credentials.access_token

    def get_all_permissions(self):
        '''Get the list of all builtin permissions.
        Returns:
            List of all builtin permissions.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._PERMISSIONS)
        response = self._session.get(uri, headers=self._header,
                                          auth=self._auth)

        if response.status_code is 200:
            permissions = []
            for p in response.json():
                permissions.append(Permission(p))
            logging.info('Successfully found builtin permissions.')
            return permissions
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_permission(self, permissionId):
        '''Get a single builtin perission by id.
        Args:
            permissionId (str) : builtin perission unique identifier
        Returns:
            A builtin perission.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._PERMISSION).format(permissionId)
        response = self._session.get(uri, headers=self._header,
                                          auth=self._auth)

        if response.status_code is 200:
            logging.info('Found perission with id {}'.format(permissionId))
            return Permission(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_all_builtin_roles(self):
        '''Get the list of the builtin roles.
        Returns:
            Page with the pagination data and the list of builtin roles.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._BUILTIN_ROLES)
        response = self._session.get(uri, headers=self._header, auth=self._auth)

        if response.status_code == 200:
            ls = []
            for l in response.json():
                ls.append(BuiltInRole(l))
            logging.info('Found {} builtin roles.'.format(len(ls)))
            return ls
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_all_custom_roles(self,
                             filter_fields=None,
                             start_index=0,
                             count=100):
        '''Get the list of the custom roles.
        Args:
            filter_fields (Filter) : utils.Filter class to filter out
                                     the result.
            start_index (int)      : 0-based pagination start index
            count (int)            : pagination page size, max 500,
                                     100 by default
        Returns:
            Page with the pagination data and the list of custom roles.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        params = su.generate_parameters(filter_fields, start_index, count)

        uri = su.uri(self._server, self._CUSTOM_ROLES)
        response = self._session.get(uri, params=params,
                                          headers=self._header,
                                          auth=self._auth)

        if response.status_code == 200:
            ls = []
            for l in response.json()['resources']:
                ls.append(CustomRole(l))
            page = Page(response.json(), ls)
            logging.info('Found {} custom roles'.format(len(ls)))
            return page
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create_custom_role(self, role):
        '''Create new custom role.
        Args:
            role (CustomRole) : custom role to create.
        Returns:
            New role object.
        Raises:
            TrivoreIDSDKException if the type of the CustomRole is wrong
            TrivoreIDException if the status code is not 201.
        '''
        if 'CustomRole' not in str(type(role)):
            raise TrivoreIDSDKException('CustomRole type is wrong!')

        uri = su.uri(self._server, self._CUSTOM_ROLES)
        response = self._session.post(uri, json=role.serialize(),
                                           headers=self._header,
                                           auth=self._auth)

        if response.status_code == 201:
            role = CustomRole(response.json())
            logging.info('Successfully created custom role with id {}'
                                                    .format(role.id))
            return role
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_custom_role(self, roleId):
        '''Get the single custom role by id.
        Args:
            roleId (str) : custom role unique identifier
        Returns:
            A custom role.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._CUSTOM_ROLE).format(roleId)
        response = self._session.get(uri, headers=self._header, auth=self._auth)

        if response.status_code is 200:
            logging.info('Found custom role with id {}'.format(roleId))
            return CustomRole(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update_custom_role(self, role, roleId=None):
        '''Modify a custom role.
        Args:
            role (CustomRole) : custom role to modify.
            roleId (str)        : if None, then role ID from the
                                          CustomRole object will be used.
        Returns:
            Modified custom role object.
        Raises:
            TrivoreIDSDKException if the type of the CustomRole is wrong
            TrivoreIDException if the status code is not 200.
        '''
        if 'CustomRole' not in str(type(role)):
            raise TrivoreIDSDKException('CustomRole type is wrong!')

        if roleId is None:
            roleId = role.id

        uri = su.uri(self._server, self._CUSTOM_ROLE).format(roleId)
        response = self._session.put(uri, json=role.serialize(),
                                          headers=self._header,
                                          auth=self._auth)

        if response.status_code is 200:
            ls = CustomRole(response.json())
            logging.info('Successfully modified custom role with the id {}'
                        .format(ls.id))
            return ls
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete_custom_role(self, roleId):
        '''Delete custom role by id.
        Args:
            roleId (str) : custom role unique identifier
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        uri = su.uri(self._server, self._CUSTOM_ROLE).format(roleId)
        response = self._session.delete(uri, headers=self._header,
                                             auth=self._auth)

        if response.status_code is 204:
            logging.info('Successfully deleted custom role with id {}'
                                                    .format(roleId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)
