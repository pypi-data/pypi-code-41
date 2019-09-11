#!/usr/bin/env python
# coding: utf-8

import requests
import json
import logging

import trivoreid.utils.service_utils as su
from trivoreid.models.datastorage import DataStorage
from trivoreid.models.page import Page
from trivoreid.exceptions import TrivoreIDSDKException, TrivoreIDException

class DataStorageService(object):
    '''
    Class to wrap datastorage API
    '''

    _DATASTORAGES = 'api/rest/v1/datastorage'
    _DATASTORAGE = 'api/rest/v1/datastorage/{}'
    _DATASTORAGE_DATA = 'api/rest/v1/datastorage/{}/data'
    _DATASTORAGE_DATA_KEY = 'api/rest/v1/datastorage/{}/data/{}'

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
                dsfilter=None,
                datafilter=None,
                start_index=0,
                count=100):
        '''Get the list of the datastorages.
        Args:
            dsfilter (Filter)      : filter out by datastorage fields.
            datafilter (Filter)    : filter out by data keys and values.
            start_index (int)      : 0-based pagination start index
            count (int)            : pagination page size, max 500
        Returns:
            Page with the pagination data and the list of datastorages.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        params = {}

        if (dsfilter != None):
            params['dsfilter'] = dsfilter.generate()

        if (datafilter != None):
            params['datafilter'] = datafilter.generate()

        if (start_index != None):
            params['startIndex'] = start_index

        if (count != None):
            params['count'] = count

        response = self._session.get(su.uri(self._server, self._DATASTORAGES),
                                params=params,
                                headers=self._auth_header,
                                auth=self._auth)

        if response.status_code is 200:
            logging.info('Found {} datastorages'.format(
                                    len(response.json()['resources'])))
            datastorages = []
            for ds in response.json()['resources']:
                datastorages.append(DataStorage(storage_fields = ds))
            page = Page(response.json(), datastorages)
            return page
        else:
            logging.info('Failed to fild datastorages')
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create(self, datastorage):
        '''Create new Data Storage.
        Args:
            datastorage (DataStorage) : data storage to create. Must contain
                                        name. If data is defined, it will be
                                        added to the new datastorage.
        Returns:
            New data storage object.
        Raises:
            TrivoreIDException if the status code is not 201.
        '''
        if 'DataStorage' not in str(type(datastorage)):
            raise TrivoreIDSDKException('DataStorage type is wrong!')

        if bool(datastorage.name) is False:
                raise TrivoreIDSDKException('Datastorage name was not defined!')

        response = self._session.post(su.uri(self._server, self._DATASTORAGES),
                                json=datastorage.serialize(),
                                headers=self._auth_header,
                                auth=self._auth)

        if response.status_code == 201:
            new_ds = DataStorage(storage_fields=response.json())
            logging.info('Successfully created datastorage with id {}'.format(
                                new_ds.id))

            if datastorage.data is not None:
                self.update_data(new_ds.id, datastorage.data)

            return new_ds
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get(self, dsId):
        '''Get the datastorage settings by id.
        Args:
            dsId (str) : datasrorage unique identifier
        Returns:
            Datastorage object (settings only).
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.get(
                            su.uri(self._server, self._DATASTORAGE).format(dsId),
                            headers=self._auth_header,
                            auth=self._auth)

        if response.status_code is 200:
            logging.info('Found datastorage with id {}'.format(dsId))
            return DataStorage(storage_fields=response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update(self, datastorage):
        '''Update existing datastorage.
        Args:
            datastorage (DataStorage) : Update datastorage data and settings.
        Returns:
            Modified datastorage object (settings only).
        Raises:
            TrivoreIDException if the status code is not 200.
        '''

        if 'DataStorage' not in str(type(datastorage)):
            raise TrivoreIDSDKException('DataStorage type is wrong!')

        if bool(datastorage.id) is False:
            raise TrivoreIDSDKException('DataStorage id was not defined!')

        response = self._session.put(su.uri(self._server, self._DATASTORAGE)
                                                    .format(datastorage.id),
                                    json = datastorage.serialize(),
                                    headers=self._auth_header,
                                    auth=self._auth)

        if response.status_code is 200:
            storage = DataStorage(storage_fields=response.json())
            logging.info('Successfully updated datastorage with id {}'.format(storage.id))

            if datastorage.data != None:
                self.update_data(storage.id, datastorage.data)

            return storage
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete(self, dsId):
        '''Delete existing datastorage.
        Args:
            dsId (sr) : datastorage ID to delete
        Returns:
            Modified datastorage object (settings only).
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.delete(su.uri(self._server, self._DATASTORAGE)
                                                    .format(dsId),
                                    headers=self._auth_header,
                                    auth=self._auth)

        if response.status_code is 204:
            logging.info('Deleted datastorage with id {}'.format(dsId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_data(self, dsId):
        '''Get data from the datastorage.
        Args:
            dsId (str) : datastorage unique identifier
        Returns:
            Json data.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.get(
                su.uri(self._server, self._DATASTORAGE_DATA).format(dsId),
                headers=self._auth_header,
                auth=self._auth)

        if response.status_code is 200:
            logging.info('Found data in the datastorage with id {}'.format(dsId))
            return response.content
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update_data(self, dsId, data):
        '''Update data in the datastorage.
        Args:
            dsId (str)  : datastorage unique identifier
            data (dict) : data to update
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        response = self._session.put(
                    su.uri(self._server, self._DATASTORAGE_DATA).format(dsId),
                    json = data,
                    headers=self._auth_header,
                    auth=self._auth)

        if response.status_code != 204:
            raise TrivoreIDException(
                                su.error_response_message(response),
                                response.status_code)
        else:
            logging.info('Successfully updated the data in the datastorage with id {}'
                                        .format(dsId))

    def get_value(self, dsId, key):
        '''Get a single value from the datastorage by the key.
        Args:
            dsId (str) : datastorage unique identifier
        Returns:
            Json data.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._DATASTORAGE_DATA_KEY).format(dsId, key)
        response = self._session.get(uri,
                                    headers=self._auth_header,
                                    auth=self._auth)

        if response.status_code is 200:
            logging.info('Found value in the datastorage with id {} and key {}'
                                                            .format(dsId, key))
            return json.loads(response.content)['value']
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update_value(self, dsId, key, value):
        '''Update a single value value in the datastorage by key.
        Args:
            dsId (str)  : datastorage unique identifier
            data (dict) : data to update
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        response = self._session.put(
             su.uri(self._server, self._DATASTORAGE_DATA_KEY).format(dsId, key),
                       json ={'value' : value},
                       headers=self._auth_header,
                       auth=self._auth)

        if response.status_code == 204:
            logging.info('Successfully updated a single value in'
                    +' the datastorage with id {} and key {}'.format(dsId, key))
        else:
            raise TrivoreIDException(
                                su.error_response_message(response),
                                response.status_code)

    def delete_value(self, dsId, key):
        '''Delete/clear single value by key.
        Args:
            dsId (str) : datastorage ID
            key (str)  : the key to clear value from
        Returns:
            Modified datastorage object (settings only).
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.delete(
                        su.uri(self._server, self._DATASTORAGE_DATA_KEY)
                                        .format(dsId, key),
                       headers=self._auth_header,
                       auth=self._auth)

        if response.status_code is 204:
            logging.info('Deleted value from the datastorage with id {} and the key {}'
                                                    .format(dsId, key))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)
