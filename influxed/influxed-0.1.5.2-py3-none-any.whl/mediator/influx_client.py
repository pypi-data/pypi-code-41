#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: influx_client.py
 File Created: Sunday, 24th February 2019 7:49:29 pm
 Author: ESR - Romeren (emilromer@hotmail.com)
 -----
 Copyright 2019 OpenSourced, OpenSourced
 -----
 Last Modified:
 Date	By	Comments
 -----
"""

import logging
import gzip
import base64

from influxed.mediator.response_parser import default_parser


from influxed.mediator.retry_strategies import NoRetryStrategy
from influxed.mediator.client_wrappers.requests_wrapper import RequestsWrapper
from influxed.mediator.exceptions import ActionNotAllowed


class InfluxClient(object):
    """
        Class definition of a influx client;
        Basicly a object that can transmit a query statement to
         an influx server and recieve a response.
        
        Can be seen as a session object
    """
    known_clients = {
        'requests': RequestsWrapper
    }    

    def __init__(self, connection_string, username, password, **kwargs):
        default_args = dict(
            client=None,
            client_parameters={},
            retry_strategy=NoRetryStrategy,
            transaction_mode=False,
            response_parser=default_parser(),
            gzip=True,
            msgpack=False,
            request_parameters={}
        )
        default_args.update(kwargs)
        self.logger = logging.getLogger('InfluxedClient')
        self.client = None
        self.clientInstance = None
        self.connection_string = connection_string
        self.username = username
        self.password = password
        self.client_parameters = default_args['client_parameters']
        self.set_connection_client(default_args['client'])
        self.retry_strategy = default_args['retry_strategy'](self)
        self.response_parser = default_args['response_parser']
        self.request_parameters = default_args['request_parameters']
        self.transaction_mode = default_args['transaction_mode']
        self.__use_gzip__ = default_args['gzip']
        self.__use_msgpack__ = default_args['msgpack']
        self.__headers__ = None
        self.batch_stack = []
    
    def set_connection_client(self, client):
        """
            Default client connection class
        """
        if(client is None):
            import requests
            client = requests
        if(client.__name__ in self.known_clients):
            c = self.known_clients[client.__name__]
            c.client = client
            self.client = c
            return
        self.client = client

    @property
    def url(self):
        return self.connection_string

    @property
    def method(self):
        return 'POST'

    @property
    def headers(self):
        if(self.__headers__ is None):
            Adapter_credentials = "{user}:{password}".format(user=self.username, password=self.password)
            Adapter_credentials_encoded = base64.b64encode(bytes(Adapter_credentials, 'utf-8'))
            self.__headers__ = {
                "Authorization": "Basic " + Adapter_credentials_encoded.decode("utf-8"),
                "Accept": "*/*",
                "Content-Type": "application/x-www-form-urlencoded",
            }
            if(self.__use_gzip__):
                self.__headers__['Content-Encoding'] = 'gzip'
                self.__headers__['Accept-Encoding'] =  'gzip'
            if(self.__use_msgpack__):
                self.__headers__['Accept'] = 'application/x-msgpack'

        return self.__headers__

    def open(self):
        """
            Open a connection to the influx server
        """
        if(self.clientInstance is None):
            self.clientInstance = self.client(**self.client_parameters)
        return self.clientInstance
    
    def close(self):
        """
            Close the session the the influx server
        """
        if(self.clientInstance is None):
            self.clientInstance = None
    
    def flush(self):
        """
            FLush whatever issnt sent to the server
        """
        result = [self.__send__(*x) for x in self.batch_stack]
        self.batch_stack = []
        return result

    def __log_send__(self, url_slug, query):
        self.logger.debug('Sending statement to ' + self.url + url_slug)
        self.logger.debug('QUERY "'+query+'"')
        self.logger.debug('METHOD "'+self.method+'"')
        self.logger.debug('HEADERS "'+ str(self.headers) +'"')

    def __handle_error__(self, query, exception):
        log_msg = "Fetch error " + str(exception)
        if(hasattr(exception, 'response')):
            log_msg += ' response '+exception.response
        self.logger.error(log_msg)
        self.logger.info('Query affected by error ' + query)

    def __send__(self, url_slug, query):
        """
            Sent whatever to the server
        """
        self.__log_send__(url_slug, query)
        try:
            response = self.open().fetch(
                self.url + url_slug,
                body=query,
                method=self.method, 
                headers=self.headers,
                **self.request_parameters
            )
            return self.response_parser.parse(response)
        except ConnectionRefusedError as e:
            raise e
        except OSError as e:
            raise e
        except Exception as e:
            if(hasattr(e, 'code') and getattr(e, 'code') in (401, 403)):
                # Http error 401: Invalid credentials
                # HTTP error 403: Forbidden
                raise ActionNotAllowed(e, 'Please verify conmnection-string ('+self.url + url_slug+'), username ('+self.username+') and password')
            self.__handle_error__(query, e)
            return self.retry_strategy.retry(query)

    def fetch(self, url_slug, query):
        """
            Syncronized fetching of a query
        """
        if(self.transaction_mode):
            self.batch_stack.append((url_slug, query))
            return None
        return self.__send__(url_slug, query)
