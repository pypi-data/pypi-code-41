#!/usr/bin/env python
# coding: utf-8

import requests
import logging

import trivoreid.utils.service_utils as su
from trivoreid.utils.criteria import Filter
from trivoreid.models.namespace import Namespace
from trivoreid.models.groups import Group
from trivoreid.models.page import Page
from trivoreid.exceptions import TrivoreIDSDKException, TrivoreIDException

class NamespaceService(object):
    '''
    Class to wrap /namespace API
    '''

    _NAMESPACES = 'api/rest/v1/namespace'
    _NAMESPACE = 'api/rest/v1/namespace/{}'

    def __init__(self, credentials, group_service):
        self._group_service = group_service
        self._server = credentials.server

        if credentials.oidc_client is None:
            self._session = requests
            self._auth = credentials.auth
        else:
            self._session = credentials.oidc_client
            self._auth = None

        self._auth_header = credentials.access_token

    def get_all(self,
                filter_fields = None,
                start_index = 0,
                count = 100,
                all_namespaces=True):
        '''Get the list of the namespaces.
        Args:
            all_namespaces (bool)  : set True to list all namespaces. When
                                     False only accessible namespaces will be
                                     listed
            filter_fields (Filter) : utils.Filter class to filter out
                                     the result.
            start_index (int)      : 0-based pagination start index
            count (int)            : pagination page size, max 500,
                                     100 by default
        Returns:
            Page with the pagination data and the list of namespaces.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''

        params = su.generate_parameters(filter_fields, start_index, count)
        params['all'] = all_namespaces

        response = self._session.get(su.uri(self._server, self._NAMESPACES),
                                params=params,
                                headers=self._auth_header,
                                auth=self._auth)

        if response.status_code == 200:
            logging.info('Found {} namespaces'.format(
                        len(response.json()['resources'])))
            namespaces = []
            for n in response.json()['resources']:
                namespaces.append(Namespace(n))
            page = Page(response.json(), namespaces)
            return page
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create(self, namespace):
        '''Create new namespace.
        Args:
            namespace (Namespace) : namespace to create.
        Returns:
            New namespace object.
        Raises:
            TrivoreIDSDKException if the type of the Namespace is wrong
            TrivoreIDException if the status code is not 201.
        '''
        if 'Namespace' not in str(type(namespace)):
            raise TrivoreIDSDKException('Namespace type is wrong!')

        response = self._session.post(su.uri(self._server, self._NAMESPACES),
                                json=namespace.serialize(True),
                                headers=self._auth_header,
                                auth=self._auth)

        if response.status_code == 201:
            ns = Namespace(response.json())
            logging.info('Successfully created namespace with id {}'.format(
                                ns.id))
            return ns
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update(self, namespace):
        '''Modify existing namespace.
        Args:
            namespace (Namespace) : namespace to modify. must contain id or
                                    code of the namespace.
        Returns:
            Modified namespace object.
        Raises:
            TrivoreIDSDKException if the type of the Namespace is wrong
            TrivoreIDException if the status code is not 200.
        '''
        if 'Namespace' not in str(type(namespace)):
            raise TrivoreIDSDKException('Namespace type is wrong!')

        if ('id' and 'code' not in namespace.serialize().keys()
                or (bool(namespace.id) is False
                    and bool(namespace.code) is False)):
            raise TrivoreIDSDKException('Should be defined code or ID!')

        if namespace.id is None:
            idOrCode = namespace.code
        else:
            idOrCode = namespace.id

        response = self._session.put(
                         su.uri(self._server, self._NAMESPACE).format(idOrCode),
                         json=namespace.serialize(True),
                         headers=self._auth_header,
                         auth=self._auth)

        if response.status_code == 200:
            ns = Namespace(response.json())
            logging.info('Successfully modified namespace with id {}'.format(
                                ns.id))
            return ns
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get(self, idOrCode):
        '''Get the single namespace by its id or code.
        Args:
            idOrCode (str) : namespace's unique identifier or code
        Returns:
            A namespace.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.get(
                    su.uri(self._server, self._NAMESPACE).format(idOrCode),
                    headers=self._auth_header,
                    auth=self._auth)

        if response.status_code == 200:
            logging.info('Found namespace with {}'.format(idOrCode))
            return Namespace(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def check_namespace_for_groups(self, nsCode, group_names):
        '''
        Check if namespace has all defined groups. If not - create.
        Args:
            nsCode (str)       : namespace code
            group_names (list) : list of group names to check
        '''
        if type(group_names) is str:
            group_names = [group_names]

        ### Check if namespace exists
        namespaces = self.get_all(Filter(Filter.EQUAL, 'code', nsCode)).resources

        if len(namespaces) is 0:
            raise TrivoreIDException(
                    'There is no namespace with the nsCode {}'.format(nsCode))
        elif len(namespaces) is 1:
            group_list = self._group_service.get_all(
                                Filter(Filter.EQUAL, 'nsCode', nsCode)).resources

            for name in group_names:
                if not group_list.check_group_name(name):
                    self._group_service.create(Group({
                            'name' : name,
                            'nsCode' : nsCode
                        }))
        else:
           raise TrivoreIDException(
                'There are more than two namespaces with the code {}'
                            .format(nsCode))

    def delete(self, idOrCode):
        '''Delete namespace by id or code.
        Args:
            idOrCode (str) : namespace id or code
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        response = self._session.delete(
                    su.uri(self._server, self._NAMESPACE).format(idOrCode),
                    headers=self._auth_header,
                    auth=self._auth)

        if response.status_code is 204:
            logging.info('Successfully deleted namespace with idOrCode {}'
                                                            .format(idOrCode))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)
