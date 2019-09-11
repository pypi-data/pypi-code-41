#!/usr/bin/env python
# coding: utf-8

import requests
import json
import logging

import trivoreid
import trivoreid.utils.service_utils as su
from trivoreid.models.authorisation import Authorisation, AuthorisationType, AuthorisationGrantRight
from trivoreid.models.page import Page
from trivoreid.exceptions import TrivoreIDSDKException, TrivoreIDException

class AuthorisationService(object):
    '''
    Class to wrap Trivore ID Authorisation API
    '''

    _AUTHS = 'api/rest/v1/authorisation'
    _AUTH = 'api/rest/v1/authorisation/{}'
    _AUTH_TYPES = 'api/rest/v1/authorisation_type'
    _AUTH_TYPE = 'api/rest/v1/authorisation_type/{}'
    _AUTH_SOURCES = 'api/rest/v1/authorisation_source'
    _AUTH_SOURCE = 'api/rest/v1/authorisation_source/{}'
    _REVOKE = 'api/rest/v1/authorisation/{}/revoke'
    _AUTH_GRANTS = 'api/rest/v1/authorisation_grant_right'
    _AUTH_GRANT = 'api/rest/v1/authorisation_grant_right/{}'
    _AUTH_GRANT_REVOKE = 'api/rest/v1/authorisation_grant_right/{}/revoke'

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
        '''Get the list of authorisations from all accessible namespaces.
        Args:
            filter_fields (Filter) : filter out the result.
            start_index (int)      : 0-based pagination start index
            count (int)            : pagination page size, max 500
        Returns:
            Page with the pagination data and the list of authorisations.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        params = su.generate_parameters(filter_fields, start_index, count)
        uri = su.uri(self._server, self._AUTHS)
        response = self._session.get(uri, params=params,
                                          headers=self._auth_header,
                                          auth=self._auth)

        if response.status_code is 200:
            auths = []
            for auth in response.json()['resources']:
                auths.append(Authorisation(auth))
            page = Page(response.json(), auths)
            logging.info('Found {} authorisations'.format(
                                            len(page.resources)))
            return page
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create(self, authorisation):
        '''Create new authorisation.
        Args:
            authorisation (Authorisation): authorisation to create.
        Returns:
            New authorisation object.
        Raises:
            TrivoreIDException    if the status code is not 201.
            TrivoreIDSDKException if the type of the Authorisation is wrong.
        '''
        if type(authorisation) != trivoreid.models.authorisation.Authorisation:
            raise TrivoreIDSDKException('Authorisation type is wrong!')

        response = self._session.post(
                                su.uri(self._server, self._AUTHS),
                                json = authorisation.serialize(),
                                headers=self._auth_header,
                                auth=self._auth)

        if response.status_code == 201:
            auth = Authorisation(response.json())
            logging.info('Successfully created authorisation with id {}'.format(
                                auth.id))
            return auth
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get(self, authId):
        '''Get a single authorisation by id.
        Args:
            authId (str) : authorisation's unique identifier
        Returns:
            An authorisation.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.get(
                            su.uri(self._server, self._AUTH).format(authId),
                            headers=self._auth_header,
                            auth=self._auth)

        if response.status_code is 200:
            logging.info('Found authorisation with id {}'.format(authId))
            return Authorisation(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update(self, authorisation, authId=None):
        '''Update existing authorisation.
        Args:
            authorisation (Authorisation)  : authorisation to modify.
            authId (str)                   : if None, then authorisation ID from
                                             the Authorisation object will
                                             be used.
        Returns:
            Modified authorisation object.
        Raises:
            TrivoreIDException if the status code is not 200.
            TrivoreIDSDKException if the type of the authorisation is wrong.
        '''
        if type(authorisation) != trivoreid.models.authorisation.Authorisation:
            raise TrivoreIDSDKException('Authorisation type is wrong!')

        if authId is None:
            authId = authorisation.id

        response = self._session.put(
                    su.uri(self._server, self._AUTH).format(authId),
                    json = authorisation.serialize(),
                    headers=self._auth_header,
                    auth=self._auth)

        if response.status_code is 200:
            auth = Authorisation(response.json())
            logging.info('Successfully modified authorisation with the id {}'
                        .format(auth.id))
            return auth
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete(self, authId):
        '''Delete authorisation by id.
        Args:
            authId (str) : authorisation's unique identifier
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        response = self._session.delete(
                    su.uri(self._server, self._AUTH).format(authId),
                    headers=self._auth_header,
                    auth=self._auth)

        if response.status_code is 204:
            logging.info('Successfully deleted authorisation with id {}'.format(authId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def revoke(self, authId):
        '''Revoke authorisation.
        Args:
            authId (str) : authorisation's unique identifier
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.post(
                    su.uri(self._server, self._REVOKE).format(authId),
                    headers=self._auth_header,
                    auth=self._auth)

        if response.status_code is 200:
            logging.info('Successfully revoked authorisation with id {}'.format(authId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_all_types(self,
                      filter_fields=None,
                      start_index=0,
                      count=100):
        '''Get the list of authorisation types from all accessible namespaces.
        Args:
            filter_fields (Filter) : filter out the result.
            start_index (int)      : 0-based pagination start index
            count (int)            : pagination page size, max 500
        Returns:
            Page with the pagination data and the list of authorisation types.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        params = su.generate_parameters(filter_fields, start_index, count)
        response = self._session.get(
                                su.uri(self._server, self._AUTH_TYPES),
                                params=params,
                                headers=self._auth_header,
                                auth=self._auth)

        if response.status_code is 200:
            types = []
            for type in response.json()['resources']:
                types.append(AuthorisationType(type))
            page = Page(response.json(), types)
            logging.info('Found {} authorisation types'.format(
                                            len(page.resources)))
            return page
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create_type(self, authType):
        '''Create new authorisation type.
        Args:
            authType (AuthorisationType): authorisation type to create.
        Returns:
            New authorisation type object.
        Raises:
            TrivoreIDException    if the status code is not 201.
            TrivoreIDSDKException if the type of the Authorisation is wrong.
        '''
        if type(authType) != trivoreid.models.authorisation.AuthorisationType:
            raise TrivoreIDSDKException('AuthorisationType type is wrong!')

        response = self._session.post(
                                su.uri(self._server, self._AUTH_TYPES),
                                json=authType.serialize(),
                                headers=self._auth_header,
                                auth=self._auth)

        if response.status_code == 201:
            auth_type = AuthorisationType(response.json())
            logging.info('Successfully created authorisation type with id {}'.format(
                                auth_type.id))
            return auth_type
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_type(self, typeId):
        '''Get a single authorisation type by id.
        Args:
            typeId (str) : authorisation type's unique identifier
        Returns:
            An authorisation type.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.get(
                        su.uri(self._server, self._AUTH_TYPE).format(typeId),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 200:
            logging.info('Found authorisation type with id {}'.format(typeId))
            return AuthorisationType(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update_type(self, authType, typeId=None):
        '''Update existing authorisation type.
        Args:
            authType (AuthorisationType)  : authorisation type to modify.
            typeId (str)                  : if None, then user ID from the
                                            authType object will be used.
        Returns:
            Modified authorisation type object.
        Raises:
            TrivoreIDException if the status code is not 200.
            TrivoreIDSDKException if the type of the user is wrong.
        '''
        if type(authType) != trivoreid.models.authorisation.AuthorisationType:
            raise TrivoreIDSDKException('AuthorisationType type is wrong!')

        if typeId is None:
            typeId = authType.id

        response = self._session.put(
                        su.uri(self._server, self._AUTH_TYPE).format(typeId),
                        json = authType.serialize(),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 200:
            auth_type = AuthorisationType(response.json())
            logging.info('Successfully modified authorisation type with the id {}'
                        .format(auth_type.id))
            return auth_type
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete_type(self, typeId):
        '''Delete authorisation type by id.
        Args:
            typeId (str) : authorisation type's unique identifier
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        response = self._session.delete(
                        su.uri(self._server, self._AUTH_TYPE).format(typeId),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 204:
            logging.info('Successfully deleted authorisation type with id {}'.format(typeId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_all_sources(self,
                        filter_fields=None,
                        start_index=0,
                        count=100):
        '''Get the list of authorisation sources from all accessible namespaces.
        Args:
            filter_fields (Filter) : filter out the result.
            start_index (int)      : 0-based pagination start index
            count (int)            : pagination page size, max 500
        Returns:
            Page with the pagination data and the list of authorisation sources.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        params = su.generate_parameters(filter_fields, start_index, count)
        response = self._session.get(
                                su.uri(self._server, self._AUTH_SOURCES),
                                params=params,
                                headers=self._auth_header,
                                auth=self._auth)

        if response.status_code is 200:
            sources = []
            for source in response.json()['resources']:
                sources.append(AuthorisationType(source))
            page = Page(response.json(), sources)
            logging.info('Found {} authorisation sources'.format(
                                            len(page.resources)))
            return page
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create_source(self, source):
        '''Create new authorisation source.
        Args:
            source (AuthorisationType): authorisation source to create.
        Returns:
            New authorisation source object.
        Raises:
            TrivoreIDException    if the status code is not 201.
            TrivoreIDSDKException if the type of the Authorisation is wrong.
        '''
        if type(source) != trivoreid.models.authorisation.AuthorisationType:
            raise TrivoreIDSDKException('Authorisation source type is wrong!')

        response = self._session.post(
                                su.uri(self._server, self._AUTH_SOURCES),
                                json=source.serialize(),
                                headers=self._auth_header,
                                auth=self._auth)

        if response.status_code == 201:
            auth_source = AuthorisationType(response.json())
            logging.info('Successfully created authorisation type with id {}'.format(
                                auth_source.id))
            return auth_source
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_source(self, sourceId):
        '''Get a single authorisation source by id.
        Args:
            typeId (str) : authorisation source's unique identifier
        Returns:
            An authorisation source.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.get(
                      su.uri(self._server, self._AUTH_SOURCE).format(sourceId),
                      headers=self._auth_header,
                      auth=self._auth)

        if response.status_code is 200:
            logging.info('Found authorisation source with id {}'.format(sourceId))
            return AuthorisationType(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update_source(self, source, sourceId=None):
        '''Update existing authorisation source.
        Args:
            source (AuthorisationType)  : authorisation type to modify.
            sourceId (str)              : if None, then user ID from the source
                                          object will be used.
        Returns:
            Modified authorisation type object.
        Raises:
            TrivoreIDException if the status code is not 200.
            TrivoreIDSDKException if the type of the user is wrong.
        '''
        if type(source) != trivoreid.models.authorisation.AuthorisationType:
            raise TrivoreIDSDKException('Authorisation source type is wrong!')

        if sourceId is None:
            sourceId = source.id

        response = self._session.put(
                    su.uri(self._server, self._AUTH_SOURCE).format(sourceId),
                    json = source.serialize(),
                    headers=self._auth_header,
                    auth=self._auth)

        if response.status_code is 200:
            auth_source = AuthorisationType(response.json())
            logging.info('Successfully modified authorisation type with the id {}'
                        .format(auth_source.id))
            return auth_source
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete_source(self, sourceId):
        '''Delete authorisation source by id.
        Args:
            sourceId (str) : authorisation source's unique identifier
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        response = self._session.delete(
                        su.uri(self._server, self._AUTH_SOURCE).format(sourceId),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 204:
            logging.info('Successfully deleted authorisation source with id {}'.format(sourceId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_all_grant_rights(self,
                             filter_fields=None,
                             start_index=0,
                             count=100):
        '''Get the list of authorisation grant rights from all accessible namespaces.
        Requires OAuth.
        Args:
            filter_fields (Filter) : filter out the result.
            start_index (int)      : 0-based pagination start index
            count (int)            : pagination page size, max 500
        Returns:
            Page with the pagination data and the list of grant rights.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        params = su.generate_parameters(filter_fields, start_index, count)
        response = self._session.get(
                        su.uri(self._server, self._AUTH_GRANTS),
                        params=params,
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 200:
            rights = []
            for right in response.json()['resources']:
                rights.append(AuthorisationGrantRight(right))
            page = Page(response.json(), rights)
            logging.info('Found {} authorisation grant rights'.format(
                                            len(page.resources)))
            return page
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create_grant_right(self, right):
        '''Create new authorisation grant right. Requires OAuth.
        Args:
            right (AuthorisationGrantRight): authorisation grant right to create.
        Returns:
            New authorisation right grant object.
        Raises:
            TrivoreIDException    if the status code is not 201.
            TrivoreIDSDKException if the type of the Authorisation is wrong.
        '''
        if type(right) != trivoreid.models.authorisation.AuthorisationGrantRight:
            raise TrivoreIDSDKException('Authorisation grant right type is wrong!')

        response = self._session.post(
                        su.uri(self._server, self._AUTH_GRANTS),
                        json=right.serialize(),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code == 201:
            grant_right = AuthorisationGrantRight(response.json())
            logging.info('Successfully created authorisation grant right with id {}'.format(
                                grant_right.id))
            return grant_right
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_grant_right(self, grantId):
        '''Get a single authorisation grant right by id. Requires OAuth.
        Args:
            grantId (str) : authorisation grant right's unique identifier
        Returns:
            An authorisation grant right.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.get(
                    su.uri(self._server, self._AUTH_GRANT).format(grantId),
                    headers=self._auth_header,
                    auth=self._auth)

        if response.status_code is 200:
            logging.info('Found authorisation type with id {}'.format(grantId))
            return AuthorisationGrantRight(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def revoke_grant_right(self, grantId):
        '''Revoke authorisation grant right. Requires OAuth.
        Args:
            grantId (str) : authorisation grant right's unique identifier
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.post(
                su.uri(self._server, self._AUTH_GRANT_REVOKE).format(grantId),
                headers=self._auth_header,
                auth=self._auth)

        if response.status_code is 200:
            logging.info('Successfully revoked authorisation grant right with id {}'.format(grantId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)
