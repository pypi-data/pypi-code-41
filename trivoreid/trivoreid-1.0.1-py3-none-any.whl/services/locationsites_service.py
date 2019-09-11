#!/usr/bin/env python
# coding: utf-8

import requests
import logging

import trivoreid.utils.service_utils as su
from trivoreid.utils.criteria import Filter
from trivoreid.models.page import Page
from trivoreid.models.locationsite import LocationSite
from trivoreid.exceptions import TrivoreIDSDKException, TrivoreIDException

class LocationSiteService(object):
    '''
    Class to wrap Trivore ID /locationsite API
    '''

    _LOCATION_SITES = 'api/rest/v1/locationsite'
    _LOCATION_SITE = 'api/rest/v1/locationsite/{}'

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
                ascending=None,
                flat=None):
        '''Get the list of the location/sites.
        Args:
            filter_fields (Filter) : utils.Filter class to filter out
                                     the result.
            start_index (int)      : 0-based pagination start index
            count (int)            : pagination page size, max 500,
                                     100 by default
            sortBy (str)           : Sort by attribute name
            ascending (bool)       : Sort direction (ascending or descending)
            flat (bool)            : Set to true to fetch a flattened hierarchy
                                     of the location/sites
        Returns:
            Page with the pagination data and the list of location/sites.
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

        if flat != None:
            params['flat'] = flat

        response = self._session.get(
                                su.uri(self._server, self._LOCATION_SITES),
                                params=params,
                                headers=self._auth_header,
                                auth=self._auth)

        if response.status_code == 200:
            logging.info('Found {} location/sites'.format(
                        len(response.json()['resources'])))

            ls = []
            for l in response.json()['resources']:
                ls.append(LocationSite(l))
            page = Page(response.json(), ls)
            return page
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create(self, locationsite):
        '''Create new location/site.
        Args:
            locationsite (LocationSite) : location/site to create.
        Returns:
            New locationsite object.
        Raises:
            TrivoreIDSDKException if the type of the LocationSite is wrong
            TrivoreIDException if the status code is not 201.
        '''
        if 'LocationSite' not in str(type(locationsite)):
            raise TrivoreIDSDKException('LocationSite type is wrong!')

        response = self._session.post(
                                su.uri(self._server, self._LOCATION_SITES),
                                json=locationsite.serialize(),
                                headers=self._auth_header,
                                auth=self._auth)

        if response.status_code == 201:
            locationsite = LocationSite(response.json())
            logging.info('Successfully created glocationsiteroup with id {}'
                                                    .format(locationsite.id))
            return locationsite
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get(self, locationsiteId):
        '''Get the single location/site by id.
        Args:
            locationsiteId (str) : location/site unique identifier
        Returns:
            A location/site.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.get(
               su.uri(self._server, self._LOCATION_SITE).format(locationsiteId),
               headers=self._auth_header,
               auth=self._auth)

        if response.status_code is 200:
            logging.info('Found location/site with id {}'.format(locationsiteId))
            return LocationSite(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update(self, locationsite, locationsiteId=None):
        '''Modify a location/site.
        Args:
            locationsite (LocationSite) : location/site to modify.
            locationsiteId (str)        : if None, then locationsite ID from the
                                          LocationSite object will be used.
        Returns:
            Modified location/site object.
        Raises:
            TrivoreIDSDKException if the type of the LocationSite is wrong
            TrivoreIDException if the status code is not 200.
        '''
        if 'LocationSite' not in str(type(locationsite)):
            raise TrivoreIDSDKException('LocationSite type is wrong!')

        if locationsiteId is None:
            locationsiteId = locationsite.id

        response = self._session.put(
               su.uri(self._server, self._LOCATION_SITE).format(locationsiteId),
               json=locationsite.serialize(),
               headers=self._auth_header,
               auth=self._auth)

        if response.status_code is 200:
            ls = LocationSite(response.json())
            logging.info('Successfully modified location/site with the id {}'
                        .format(ls.id))
            return ls
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete(self, locationsiteId):
        '''Delete location/site by id.
        Args:
            locationsiteId (str) : location/site unique identifier
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        response = self._session.delete(
               su.uri(self._server, self._LOCATION_SITE).format(locationsiteId),
               headers=self._auth_header,
               auth=self._auth)

        if response.status_code is 204:
            logging.info('Successfully deleted location/site with id {}'
                                                    .format(locationsiteId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)
