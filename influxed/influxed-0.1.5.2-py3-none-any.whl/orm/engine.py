#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: engine.py
 File Created: Monday, 25th February 2019 9:57:17 pm
 Author: ESR - Romeren (emilromer@hotmail.com)
 -----
 Copyright 2019 OpenSourced, OpenSourced
 -----
 Last Modified:
 Date	By	Comments
 -----
"""

import logging
from influxed.mediator import Mediator
from influxed.orm.influx_server import InfluxServer
from influxed.orm.declarative.declarative_base import DecarativeBase
from influxed.ifql import select, show

class Engine(object):
    logger = logging.getLogger('influxed.engine')
    mediator = None
    servers = {}
    server = None
    influx_server_cls = InfluxServer

    def __init__(self, **kwargs):
        self.influx_server_cls = kwargs.get('influx_server_cls', self.influx_server_cls)
        self.mediator = kwargs.get('mediator', Mediator())
        self.servers = {}
        self.server = None

    def add_server(self, connection_string, username, password, reflect=False, **kwargs):
        self.mediator.add_client(connection_string, username, password, **kwargs)
        self.logger.info('Adding server connection with username=' + username + ' connection_string=' + connection_string)
        server_ = self.influx_server_cls(self.mediator, connection_string, username, password, **kwargs)
        
        self.servers[username] = server_
        self.server = server_
        declared_base = kwargs.get('declarative_base', None)
        if(reflect and declared_base):
            raise ValueError('Cannot both reflect and be declarative!')
        if(reflect):
            return server_.reflect_server()
        if(declared_base):
            return server_.create_server_from_declarative_model(declared_base)

    def remove_server(self, username):
        self.logger.info('Removing server connection with username=' + username)
        try:
            self.servers.pop(username)
        except:
            self.logger.info('Server connection with username=' + username + ' does not exist!')

    def __getattr__(self, name):
        if(name in self.servers):
            return self.servers[name]
        self.logger.error('Server "' + name + '" not found!')
        raise AttributeError

    def __getitem__(self, item):
        return self.__getattr__(item)

    def ls(self, all=False):
        for _, v in self.servers.items():
            print('Server: '+v.username+'@'+v.__connection_string__+' | use "engine.'+v.username+'"')
            if(all):
                v.ls(all, prefix='  ')

engine = Engine()