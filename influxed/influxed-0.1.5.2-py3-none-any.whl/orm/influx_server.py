#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: influx_server.py
 File Created: Sunday, 24th February 2019 8:18:49 pm
 Author: ESR - Romeren (emilromer@hotmail.com)
 -----
 Copyright 2019 OpenSourced, OpenSourced
 -----
 Last Modified:
 Date	By	Comments
 -----
"""


from influxed.orm.capabilities.showable import Showable
from influxed.orm.capabilities.createable import Creatable
from influxed.orm.capabilities.executable import Executable
from influxed.orm.capabilities.asyncable import HandlePosibleAsync

from influxed.ifql.util import KEY_WORDS
from influxed.orm.database import Database



class InfluxServer(Showable, Creatable, Executable):
    """
        class definition coresponfing to a influx server
    """

    def __init__(self, mediator, connection_string, username, password, databases=[], **kwargs):
        self.__connection_string__ = connection_string
        self.__username__ = username
        self.__mediator__ = mediator
        
        for db in databases:
            db.influx_server = self
        self.databases = {x.name: x for x in databases}

    def reflect_server(self):
        """
            Connect to db and get all database objects and instanciate internal objects
        """
        wrapper = HandlePosibleAsync(self.__look_up_databases__()) # (might be async)
        wrapper.chain_function(self.__create_orm_databases__)
        wrapper.chain_function(self.__nested_db_reflect__)
        return wrapper.return_()

    def create_server_from_declarative_model(self, model):
        possible_future = HandlePosibleAsync(self.__look_up_databases__()) # (might be async)
        self.bases = model.__subclasses__()
        possible_future.chain_function(self.__validate_and_create_measurements__)
        return possible_future.return_()

    def __validate_and_create_measurements__(self, databases):
        strict = databases.shape[0] > 1
        any_declared_databases = any([base.__database__ is not None for base in self.bases])
        strict = any_declared_databases or strict
        for base in self.bases:
            self.__validate_and_create_measurement__(databases, base, strict)

    def __validate_and_create_measurement__(self, databases, base, strict):
        if(not base.__measurement__ or base.__measurement__ is None):
                raise ValueError('Declarative measurement '+base.__name__+' does not implement __measurement__')
        elif(strict and base.__database__ not in databases.name):
            raise ValueError('Declarative measurement '+base.__name__+' refers db '+ str(base.__database__)+' but the database does not exists')
        elif(strict and base.__database__ in databases.name):
            self.__create_database_from_name__(base.__database__)
            base.set_database(self.databases[base.__database__])
            setattr(base, 'name', base.__measurement__)
            self.databases[base.__database__].__add_orm_measurement__(base)
        else:
            self.__create_database_from_name__(databases.name.iloc[0])
            base.set_database(self.databases[databases.name.iloc[0]])
            setattr(base, 'name', base.__measurement__)
            self.databases[databases.name.iloc[0]].__add_orm_measurement__(base)

    def __nested_db_reflect__(self, databases):
        possible_futures = []
        for db in databases.values():
            possible_futures.append(db.reflect()) # (might be async)
        return possible_futures

    def __look_up_databases__(self):
        """
            Important note since a influx client can be async and 
            we need to be able to handle both. We need to do some trics here :)
        """
        # Get databases:
        databases = self.show(KEY_WORDS.DATABASES).all() # (might be async)
        return databases

    def __create_orm_databases__(self, databases):
        """
            Instanciate all ORM database objects
            All sync behaviour.
        """
        if(databases is None or (not isinstance(databases, list) and databases.empty)):
            return self.databases
        
        for name in databases.name:
            self.__create_database_from_name__(name)
        return self.databases

    def __create_database_from_name__(self, name):
        if(name in self.databases):
            return
        db = Database()
        db.influx_server = self
        db.name = name
        self.databases[name] = db

    def __getattr__(self, name):
        if(name in self.databases):
            return self.databases[name]
        # self.logger.error(f'Database "{name}" not found!')
        raise AttributeError('Database "'+name+'" not found!')

    def __getitem__(self, item):
        return self.__getattr__(item)

    def ls(self, all=False, prefix=''):
        for k, v in self.databases.items():
            print(prefix+' Database '+k)
            if(all):
                v.ls(all, prefix=prefix+'  ')

    


        