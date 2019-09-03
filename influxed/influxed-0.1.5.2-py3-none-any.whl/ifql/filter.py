#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: filter.py
 File Created: Friday, 26th July 2019 3:28:52 pm
 Author: ESR - Romeren (emil@spectral.energy)
 -----
 Copyright 2019 Spectral, Spectral
 -----
 Last Modified:
 Date	By	Comments
 -----
"""

import datetime
from influxed.ifql.functions import Algebraic
from influxed.ifql.column import __time_column__

class WhereFilter(object):
    default_chaining_operator = None
    where_statements = []
    sub_filters = []
    _numeric_types = (int, float)

    def __init__(self, default_chaining_operator):
        self.where_statements = []
        self.sub_filters = []
        self.default_chaining_operator = default_chaining_operator

    @property
    def empty(self):
        if(self.where_statements):
            return False
        return True

    def add(self, field, operator, value):
        self.where_statements.append(dict(
                field=field,
                operator=operator,
                value=value
            )
        )
    
    def _format_boolean(self, val):
        if(val):
            return 'true'
        else:
            return 'false'

    def _format_value(self, value):
        if type(value) is bool:
            return self._format_boolean(value)
        elif isinstance(value, self._numeric_types):
            return "%r" % value
        elif isinstance(value, datetime.datetime):
            if value.tzinfo:
                value = value.astimezone(datetime.datetime.UTC_TZ)
            dt = datetime.datetime.strftime(value, "%Y-%m-%d %H:%M:%S.%f")
            return "'%s'" % dt[:-3]
        return "'%s'" % value

    def _format_where_expression(self, field, operator, value):
        if(isinstance(field, __time_column__)):
            return field.name + ' ' + operator._value_ + ' ' + self._format_value(value)
        return str(field) + operator._value_ + self._format_value(value)

    def _format(self):
        formatted = []
        for expression in self.where_statements:
            exp = self._format_where_expression(
                **expression
            )
            formatted.append(exp)
        formatted = "%s" % (" " + str(self.default_chaining_operator._value_) +" ").join(formatted)
        
        for x in self.sub_filters:
            formatted += ' ' + str(self.default_chaining_operator._value_) + ' (' + x._format() +')'
        return formatted
