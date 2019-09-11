#!/usr/bin/env python
# coding: utf-8

import requests
import logging

import trivoreid.utils.service_utils as su
from trivoreid.utils.criteria import Filter
from trivoreid.models.page import Page
from trivoreid.models.contact import Contact
from trivoreid.models.enterprise import Enterprise
from trivoreid.exceptions import TrivoreIDSDKException, TrivoreIDException

class ContactService(object):
    '''
    Class to wrap Trivore ID /contact API
    '''

    _CONTACTS = 'api/rest/v1/contact'
    _CONTACT = 'api/rest/v1/contact/{}'
    _ENTERPRISE = 'api/rest/v1/contact/{}/enterpriseinfo'

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
        '''Get the list of the contacts.
        Args:
            filter_fields (Filter) : utils.Filter class to filter out
                                     the result.
            start_index (int)      : 0-based pagination start index
            count (int)            : pagination page size, max 500,
                                     100 by default
        Returns:
            Page with the pagination data and the list of contacts.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        params = su.generate_parameters(filter_fields, start_index, count)

        response = self._session.get(
                                su.uri(self._server, self._CONTACTS),
                                params=params,
                                headers=self._auth_header,
                                auth=self._auth)

        if response.status_code == 200:
            logging.info('Found {} contact objects'.format(
                        len(response.json()['resources'])))

            ls = []
            for l in response.json()['resources']:
                ls.append(Contact(l))
            page = Page(response.json(), ls)
            return page
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create(self, contact):
        '''Create new contact.
        Args:
            contact (Contact) : contact to create.
        Returns:
            New contact object.
        Raises:
            TrivoreIDSDKException if the type of the Contact is wrong
            TrivoreIDException if the status code is not 201.
        '''
        if 'Contact' not in str(type(contact)):
            raise TrivoreIDSDKException('Contact type is wrong!')

        response = self._session.post(
                                su.uri(self._server, self._CONTACTS),
                                json=contact.serialize(),
                                headers=self._auth_header,
                                auth=self._auth)

        if response.status_code == 201:
            contact = Contact(response.json())
            logging.info('Successfully created contact with id {}'
                                                    .format(contact.id))
            return contact
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get(self, contactId):
        '''Get the single contact by id.
        Args:
            contactId (str) : contact unique identifier
        Returns:
            A contact.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.get(
                        su.uri(self._server, self._CONTACT).format(contactId),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 200:
            logging.info('Found contact with id {}'.format(contactId))
            return Contact(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update(self, contact, contactId=None):
        '''Modify a contact.
        Args:
            contact (Contact) : contact to modify.
            contactId (str)        : if None, then contact ID from the
                                          Contact object will be used.
        Returns:
            Modified contact object.
        Raises:
            TrivoreIDSDKException if the type of the Contact is wrong
            TrivoreIDException if the status code is not 200.
        '''
        if 'Contact' not in str(type(contact)):
            raise TrivoreIDSDKException('Contact type is wrong!')

        if contactId is None:
            contactId = contact.id

        response = self._session.put(
                        su.uri(self._server, self._CONTACT).format(contactId),
                        json=contact.serialize(),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 200:
            ls = Contact(response.json())
            logging.info('Successfully modified contact with the id {}'
                        .format(ls.id))
            return ls
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete(self, contactId):
        '''Delete contact by id.
        Args:
            contactId (str) : contact unique identifier
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        response = self._session.delete(
                        su.uri(self._server, self._CONTACT).format(contactId),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 204:
            logging.info('Successfully deleted contact with id {}'
                                                    .format(contactId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_enterprise_info(self, contactId):
        '''Get the enterprise info of the contact.
        Args:
            contactId (str) : contact unique identifier
        Returns:
            An enterprise.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.get(
                    su.uri(self._server, self._ENTERPRISE).format(contactId),
                    headers=self._auth_header,
                    auth=self._auth)

        if response.status_code is 200:
            logging.info('Found enterprise of the contact with id {}'
                                                        .format(contactId))
            return Enterprise(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update_enterprise_info(self, contactId, enterprise):
        '''Update the enterprise info of the contact.
        Args:
            contactId (str)         : contact unique identifier
            enterprise (Enterprise) : enterprise to update
        Returns:
            An updated enterprise.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        if 'Enterprise' not in str(type(enterprise)):
            raise TrivoreIDSDKException('Enterprise type is wrong!')

        response = self._session.put(
                    su.uri(self._server, self._ENTERPRISE).format(contactId),
                    json=enterprise.serialize(),
                    headers=self._auth_header,
                    auth=self._auth)

        if response.status_code is 200:
            logging.info('Successfully updated enterprise of the contact {}'
                                                        .format(contactId))
            return Enterprise(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)
