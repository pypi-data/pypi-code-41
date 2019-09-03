#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: insertable.py
 File Created: Friday, 26th July 2019 3:47:00 pm
 Author: ESR - Romeren (emil@spectral.energy)
 -----
 Copyright 2019 Spectral, Spectral
 -----
 Last Modified:
 Date	By	Comments
 -----
"""

import datetime as dt
from influxed.orm.capabilities.executable import Executable
from influxed.ifql import insert


class Insertable(Executable):

    def __build_inserts__(self, val):
        if(hasattr(self, 'name')):
            if(isinstance(val, (int, float))):
                val = (val, dt.datetime.now())
            if(isinstance(val, (tuple))):
                val, time = val
                if(isinstance(val, dt.datetime)):
                    tmp = val
                    val = time
                    time = tmp
                val = {
                    'time': time,
                    getattr(self, 'name'): val
                }
        
        statement = insert(data=val, hook=self)
        return self.__insert_prefix__(statement)

    def __insert_prefix__(self, insert_statement):
        return insert_statement

    def insert(self, val, measurement=None):
        """
            Insert int, float, double, etc. or tuple of time and value or pandas series
        """
        self.execute(self.__build_inserts__(val))

