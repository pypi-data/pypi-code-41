#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: retry_strategies.py
 File Created: Friday, 26th July 2019 3:43:28 pm
 Author: ESR - Romeren (emil@spectral.energy)
 -----
 Copyright 2019 Spectral, Spectral
 -----
 Last Modified:
 Date	By	Comments
 -----
"""

import logging


class ARetryStrategy(object):
    """
        Definition of a retry strategy
    """
    def __init__(self, influx_client):
        self.influx_client = influx_client
        self.logger = logging.getLogger('InfluxedRetryStrat')

    def retry(self, query):
        """
            Called when a request failed
        """
        raise NotImplementedError('This method has not yet been implemented')

    async def async_retry(self, query):
        """
            Retry async
        """
        raise NotImplementedError('This method has not yet been implemented')


class NoRetryStrategy(ARetryStrategy):
    """
        Implementation of a retry strategy with no retry.
    """

    def retry(self, query):
        self.logger.warning('No response returned')
        return None
    
    async def async_retry(self, query):
        return None


class RetryNTimes(ARetryStrategy):
    """
        Implementation of a retry strategy that retries n times
    """
    max_tries = 5

    def __init__(self, influx_client):
        self.number_of_tries = 0
        super(RetryNTimes, self).__init__(influx_client)
    
    def retry(self, query):
        self.number_of_tries += 1
        if(self.number_of_tries < self.max_tries):
            return self.influx_client.__send__(query)
        self.logger.info('No response returned')
        return None

    async def async_retry(self, query):
        self.number_of_tries += 1
        if(self.number_of_tries < self.max_tries):
            return await self.influx_client.__send__(query)
        self.logger.info('No response returned')
        return None
        