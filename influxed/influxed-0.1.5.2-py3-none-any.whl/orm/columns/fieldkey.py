#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: fieldkey.py
 File Created: Tuesday, 9th July 2019 4:31:25 pm
 Author: ESR - Romeren (emil@spectral.energy)
 -----
 Copyright 2019 Spectral, Spectral
 -----
 Last Modified:
 Date	By	Comments
 -----
"""

import datetime as dt
from influxed.ifql.functions import Count, Min, Max, Mean, Distinct, Percentile, Derivative, Sum, Stddev, First, Last
from influxed.ifql.column import Field
from influxed.orm.capabilities.queryable import Queryable
from influxed.orm.capabilities.insertable import Insertable


class FieldKey(Field, Queryable, Insertable):

    @property
    def database(self):
        return self.__measurement__.database

    @property
    def measurement(self):
        return self.__measurement__
    
    def set_measurement(self, val):
        self.__measurement__ = val
        return self


    def __select_prefix__(self, select_statement):
        return select_statement.from_(self.measurement.name).select(self)
