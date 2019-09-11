#!/usr/bin/env python
# coding: utf-8

import requests
import logging

import trivoreid.utils.service_utils as su
from trivoreid.utils.criteria import Filter
from trivoreid.exceptions import TrivoreIDSDKException, TrivoreIDException
from trivoreid.models.subscription import Subscription, Period
from trivoreid.models.page import Page

class SubscriptionsService(object):
    '''
    Class to wrap /subscriptions Trivore ID API.
    '''
    _SUBSCRIPTIONS = 'api/rest/v1/subscription'
    _SUBSCRIPTION = 'api/rest/v1/subscription/{}'
    _PERIODS = 'api/rest/v1/subscription/{}/period'
    _PERIOD = 'api/rest/v1/subscription/{}/period/{}'
    _TERMINATE = 'api/rest/v1/subscription/{}/terminate'

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
        '''Get the list of the subscriptions.
        Args:
            filter_fields (Filter) : filter out the result.
            start_index (int)      : 0-based pagination start index.
            count (int)            : pagination page size, max 500.
            sortBy (str)           : Sort by attribute name.
            ascending (boolean)    : Sort direction.
        Returns:
            Page with the pagination data and the list of users.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''

        params = su.generate_parameters(filter_fields, start_index, count)

        if sortBy != None:
            params['sortBy'] = sortBy

        if ascending != None:
            if ascending:
                params['sortOrder'] = 'ascending'
            else:
                params['sortOrder'] = 'descending'

        response = self._session.get(su.uri(self._server, self._SUBSCRIPTIONS),
                                params=params,
                                headers=self._auth_header,
                                auth=self._auth)

        if response.status_code is 200:
            subs = []
            for s in response.json()['resources']:
                subs.append(Subscription(s))
            page = Page(response.json(), subs)
            logging.info('Found {} subscriptions'
                                .format(page.totalResults))
            return page
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create(self, subscription):
        '''Create new subscription.
        Args:
            subscription (Subscription) : subscription to create.
        Returns:
            New subscription object.
        Raises:
            TrivoreIDSDKException if the type of the Subscription is wrong
            TrivoreIDException if the status code is not 201.
        '''
        if 'Subscription' not in str(type(subscription)):
            raise TrivoreIDSDKException('Subscription type is wrong!')

        response = self._session.post(
                            su.uri(self._server, self._SUBSCRIPTIONS),
                            json=subscription.serialize(),
                            headers=self._auth_header,
                            auth=self._auth)

        if response.status_code == 201:
            sub = Subscription(response.json())
            logging.info('Successfully created subscription with id {}'
                                                            .format(sub.id))
            return sub
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get(self, subId):
        '''Get a single subscription by its id.
        Args:
            subId (str) : subscription's unique identifier
        Returns:
            A subscription.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.get(
                    su.uri(self._server, self._SUBSCRIPTION).format(subId),
                    headers=self._auth_header,
                    auth=self._auth)

        if response.status_code == 200:
            logging.info('Found subscription with {}'.format(subId))
            return Subscription(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update(self, subscription, subscriptionId=None):
        '''Modify existing subscription.
        Args:
            subscription (Subscription) : subscription to modify.
            subscriptionId (str)        : subscription ID if it was not defined
                                          in the subscription object.
        Returns:
            Modified subscription object.
        Raises:
            TrivoreIDSDKException if the type of the Subscription is wrong
            TrivoreIDException if the status code is not 200.
        '''
        if 'Subscription' not in str(type(subscription)):
            raise TrivoreIDSDKException('Subscription type is wrong!')

        if subscriptionId == None:
            subscriptionId = subscription.id

        response = self._session.put(su.uri(self._server, self._SUBSCRIPTION)
                                                    .format(subscriptionId),
                                    json=subscription.serialize(),
                                    headers=self._auth_header,
                                    auth=self._auth)

        if response.status_code == 200:
            sub = Subscription(response.json())
            logging.info('Successfully modified subscription with id {}'
                                                            .format(sub.id))
            return sub
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create_period(self, subscriptionId, period):
        '''Create new subscription's period.
        Args:
            subscriptionId (str) : target subscription'sunique identifier.
            period (Period)      : period to create.
        Returns:
            New period object.
        Raises:
            TrivoreIDSDKException if the type of the Period is wrong
            TrivoreIDException if the status code is not 201.
        '''
        if 'Period' not in str(type(period)):
            raise TrivoreIDSDKException('Period type is wrong!')

        response = self._session.post(su.uri(self._server, self._PERIODS)
                                                .format(subscriptionId),
                                     json=period.serialize(),
                                     headers=self._auth_header,
                                     auth=self._auth)

        if response.status_code == 201:
            p = Period(response.json())
            logging.info('Successfully created period with id {}'.format(p.id))
            return p
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_period(self, subscriptionId, periodId):
        '''Get a single subscription's period by its id.
        Args:
            subscriptionId (str) : subscription's unique identifier
            periodId (str)       : period's unique identifier
        Returns:
            A period.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.get(su.uri(self._server, self._PERIOD)
                                        .format(subscriptionId, periodId),
                                     headers=self._auth_header,
                                     auth=self._auth)

        if response.status_code == 200:
            logging.info('Found period with id {} from the subscription {}'
                                        .format(periodId, subscriptionId))
            return Period(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update_period(self, subscriptionId, period, periodId=None):
        '''Modify existing subscription's period.
        Args:
            subscriptionId (str)        : subscription's unique identifier.
            period (Period)             : period to modify.
            periodId (str)              : period ID if it was not defined
                                          in the period object.
        Returns:
            Modified period object.
        Raises:
            TrivoreIDSDKException if the type of the Subscription is wrong
            TrivoreIDException if the status code is not 200.
        '''
        if 'Period' not in str(type(period)):
            raise TrivoreIDSDKException('Period type is wrong!')

        if periodId == None:
            periodId = period.id

        response = self._session.put(su.uri(self._server, self._PERIOD)
                                              .format(subscriptionId, periodId),
                                     json=period.serialize(),
                                     headers=self._auth_header,
                                     auth=self._auth)

        if response.status_code == 200:
            p = Period(response.json())
            logging.info('Successfully modified period with id {} in the subsciption {}'
                                                .format(p.id, subscriptionId))
            return p
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def terminate(self, subscriptionId, when=None):
        '''Terminate the subscription.
        Args:
            subscriptionId (str)   : subscription's unique identifier.
            when (str)             : Termination time. Current time used if
                                     not specified.
        Returns:
            Terminated subscription object.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        params = {}
        if when != None:
            params['WHEN'] = when

        response = self._session.post(su.uri(self._server, self._TERMINATE)
                                            .format(subscriptionId),
                                      params=params,
                                      headers=self._auth_header,
                                      auth=self._auth)

        if response.status_code == 200:
            sub = Subscription(response.json())
            logging.info('Successfully terminated subscription with id {}'
                                                            .format(sub.id))
            return sub
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)
