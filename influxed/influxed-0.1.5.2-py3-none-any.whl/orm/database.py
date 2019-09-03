#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: database.py
 File Created: Monday, 25th February 2019 8:14:31 pm
 Author: ESR - Romeren (emilromer@hotmail.com)
 -----
 Copyright 2019 OpenSourced, OpenSourced
 -----
 Last Modified:
 Date	By	Comments
 -----
"""
from inspect import isclass
from influxed.ifql.column import Tag
from influxed.orm.capabilities.showable import Showable
from influxed.orm.capabilities.executable import Executable
from influxed.orm.capabilities.queryable import Queryable
from influxed.orm.capabilities.insertable import Insertable
from influxed.orm.capabilities.asyncable import HandlePosibleAsync
from influxed.orm.measurement import Measurement
from influxed.ifql.util import KEY_WORDS


class Database(Showable, Insertable, Queryable, Executable):
    """
        Influx definition of a database instance
    """

    @property
    def name(self):
        return self.__db__

    @name.setter
    def name(self, value):
        self.__db__ = value

    @property
    def measurements(self):
        if(not hasattr(self, '__measurements__')):
            self.__measurements__ = {}
        return self.__measurements__
    
    @measurements.setter
    def measurements(self, value):
        self.__measurements__ = value

    @property
    def database(self):
        return self

    @property
    def influx_server(self):
        return self.__influx_server__
    
    @influx_server.setter
    def influx_server(self, server):
        self.__influx_server__ = server

    @property
    def connection_string(self):
        return self.influx_server.connection_string

    @property
    def username(self):
        return self.influx_server.username
    
    @property
    def mediator(self):
        return self.influx_server.mediator

    def __show_prefix__(self, show_statement):
        """
            Overwrite from showable
        """
        return show_statement.on(self.name)

    def __insert_prefix__(self, insert_statement):
        return insert_statement.on(self.name)

    def __getattr__(self, name):
        if(name in ('__measurements__')):
            raise AttributeError
        if(name in self.measurements):
            return self.measurements[name]
        self.__add_orm_measurement_from_name__(name)
        return self.measurements[name]

    def __getitem__(self, item):
        return self.__getattr__(item)

    def reflect(self):
        # Get and reflect measurements:
        possible_future = HandlePosibleAsync(self.show(KEY_WORDS.MEASUREMENTS).all())
        possible_future.chain_function(self.__create_orm_measurements__)
        possible_future.chain_function(self.__nested_measurement_reflect__)
        return possible_future.return_()

    def __nested_measurement_reflect__(self, measurements):
        possible_futures = []
        for measurement in measurements.values():
            possible_futures.append(measurement.reflect())
        return possible_futures

    def __create_orm_measurements__(self, measurements):
        if(measurements is None or (not isinstance(measurements, list) and measurements.empty)):
            return self.measurements
        for name in measurements.name:
            self.__add_orm_measurement_from_name__(name)    
        return self.measurements

    def __add_orm_measurement_from_name__(self, name):
        if(name in self.measurements):
            return
        m = Measurement().set_database(self)
        m.name = name
        self.__add_orm_measurement__(m)

    def __add_orm_measurement__(self, measurement):
        self.measurements[measurement.name] = measurement
        for k, v in measurement.__dict__.items():
            if(isclass(v) and issubclass(v, Tag)):
                setattr(measurement, k, v(k).set_measurement(measurement))

    def ls(self, all=False, prefix=''):
        for k, v in self.measurements.items():
            print(prefix+' Measurement '+k)
            if(all):
                v.ls(prefix=prefix+'  ')
