#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: mediator.py
 File Created: Friday, 26th July 2019 3:45:28 pm
 Author: ESR - Romeren (emil@spectral.energy)
 -----
 Copyright 2019 Spectral, Spectral
 -----
 Last Modified:
 Date	By	Comments
 -----
"""

import gzip
from urllib.parse import urlencode
from influxed.mediator.influx_client import InfluxClient
from influxed.ifql.statement import AStatement
from influxed.ifql.statement import DummyStatement
from influxed.ifql import select, show, insert


class Mediator(object):

    def __init__(self):
        self.client_map = {}
        self.max_request_size = 10000000
        self.number_of_clients = 0

    def add_client(self, connection_string, username, password, **kwargs):
        self.max_request_size = kwargs.get('max_request_size', self.max_request_size)
        if(not connection_string or not username):
            raise TypeError('Type error connection_sting '+type(connection_string)+' and username '+type(username)+' must be <str>')
        
        if(connection_string+username not in self.client_map):
            self.client_map[connection_string+username] = InfluxClient(
                connection_string,
                username, password,
                **kwargs
            )
            self.number_of_clients += 1

    def query_to_body(self, query):
        if(issubclass(type(query), AStatement)):
            return self.a_statement_query_to_body(query)
        if(isinstance(query, insert)):
            return self.instert_statement_to_body(query)
        return self.a_statement_query_to_body(query)

    def instert_statement_to_body(self, query):
        bodies = self.split_request(query.format_lines())
        bodies = [gzip.compress(b.encode()) for b in bodies]
        return [('/write?db='+query.database, b) for b in bodies]

    def split_request(self, lines):
        """
            Devides a request into too if it is too long.
        """
        length = 0
        current_index = 0
        for indx, x in enumerate(lines):
            n_l = len(x)
            if(length + n_l + 1 > self.max_request_size): # the plus one is for the added '\n'
                yield '\n'.join(lines[current_index:indx])
                current_index = indx
                length = n_l
            else:
                length += n_l + 1 # the plus one is for the added '\n'
        if(current_index < len(lines)):
            yield '\n'.join(lines[current_index:])


    def a_statement_query_to_body(self, query):
        param = {
            'q': query.format(),
            'chunked': 'true',
        }
        if(query.database):
            param['db'] = query.database
        return [('/query', urlencode(param))]


    def get_client(self, connection_string, username):
        client = None
        if((connection_string is None or username is None) and self.number_of_clients != 1):
            raise Exception('No connection_string and username specified')
        elif(connection_string is None or username is None):
            client = self.client_map[next(iter(self.client_map))]
        else:
            client = self.client_map[connection_string+username]
        return client

    def execute(self, query, connection_string=None, username=None, database=None):
        if(isinstance(query, str)):
            query = DummyStatement(query, database)
        
        query_list = self.query_to_body(query)

        if(len(query_list) == 1):
            return self.get_client(connection_string, username).fetch(*query_list[0])

        return [
            self.get_client(connection_string, username).fetch(*query_list[i])
            for i in range(len(query_list))
        ]

# mediator = Mediator()