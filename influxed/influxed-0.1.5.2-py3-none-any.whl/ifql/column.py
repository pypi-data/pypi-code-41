#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: column.py
 File Created: Tuesday, 9th July 2019 4:30:36 pm
 Author: ESR - Romeren (emil@spectral.energy)
 -----
 Copyright 2019 Spectral, Spectral
 -----
 Last Modified:
 Date	By	Comments
 -----
"""

from enum import Enum
from influxed.ifql.util import COMPARISON_OPERATOR, ARITMATIC_OPERATOR, INTERVAL, ORDER, str_needs_escape
from influxed.ifql.functions import Algebraic, Count, Min, Max, Mean, Distinct, Percentile, Derivative, Sum, Stddev, First, Last

class Column(object):
    name = None
    display_as = None

    def __init__(self, name, as_name=None):
        self.name = name
        self.display_as = as_name
        self.call_arguments = []

    def as_(self, name):
        self.display_as = name
        return self

    def __eq__(self, other):
        return dict(
            field=self,
            operator=COMPARISON_OPERATOR.eq,
            value=other
        )
    
    def __ne__(self, other):
        return dict(
            field=self,
            operator=COMPARISON_OPERATOR.neq,
            value=other
        )

    def __lt__(self, other):
        return dict(
            field=self,
            operator=COMPARISON_OPERATOR.lt,
            value=other
        )
    
    def __gt__(self, other):
        return dict(
            field=self,
            operator=COMPARISON_OPERATOR.gt,
            value=other
        )
    
    def __ge__(self, other):
        return dict(
            field=self,
            operator=COMPARISON_OPERATOR.gteq,
            value=other
        )
    
    def __le__(self, other):
        return dict(
            field=self,
            operator=COMPARISON_OPERATOR.lteq,
            value=other
        )
    
    def __add__(self, other):
        return Algebraic(self, ARITMATIC_OPERATOR.add, other)

    def __radd__(self, other):
        return Algebraic(other, ARITMATIC_OPERATOR.add, self)

    def __sub__(self, other):
        return Algebraic(self, ARITMATIC_OPERATOR.subtract, other)

    def __rsub__(self, other):
        return Algebraic(other, ARITMATIC_OPERATOR.subtract, self)

    def __mul__(self, other):
        return Algebraic(self, ARITMATIC_OPERATOR.multiply, other)

    def __rmul__(self, other):
        return Algebraic(other, ARITMATIC_OPERATOR.multiply, self)

    def __truediv__(self, other):
        return Algebraic(self, ARITMATIC_OPERATOR.devide, other)

    def __rtruediv__(self, other):
        return Algebraic(other, ARITMATIC_OPERATOR.devide, self)

    def like(self, other):
        return Algebraic(self, COMPARISON_OPERATOR.regexMatch, other)
    
    def nlike(self, other):
        return Algebraic(self, COMPARISON_OPERATOR.regexNotMatch, other)

    def __call__(self, *args):
        self.call_arguments = args
        return self

    def format(self):
        if(self.call_arguments):
            return str(self.name)+'(' + str(self.call_arguments[0]) + ')'
        else:
            formated = self.name
            if(str_needs_escape(formated)):
                formated = '"' + formated + '"'
            if(self.display_as):
                return formated + ' AS ' + self.display_as
            return formated
    
    def __str__(self):
        return self.format()

class Tag(Column):
    def count(self):
        return Count(self)

    def lirst(self):
        return First(self)
           
    def last(self):
        return Last(self)

    def distinct(self):
        return Distinct(self)

    def insert(self, val):
        """
            Insert a value
        """
        raise NotImplementedError()

class Field(Tag):
    
    def min(self):
        return Min(self)
 
    def max(self):
        return Max(self)
            
    def mean(self):
        return Mean(self)
          
    def percentile(self):
        return Percentile(self)
           
    def derivative(self):
        return Derivative(self)
            
    def sum(self):
        return Sum(self)
            
    def std(self):
        return Stddev(self)


class __time_column__(Column):
    """
        Influx's special time column
    """
    def __init__(self, n=1, unit=INTERVAL.hour):
        self.unit = INTERVAL.sec
        self.__n__, self.unit = self.parse_n(n)
        super(__time_column__, self).__init__('time', None)
        self(self.interval)

    @property
    def interval(self):
        return str(self.__n__) + self.unit.value
    
    @interval.setter
    def interval(self, value):
        n, interval = self.parse_n(value)
        self.__n__ = n
        self.unit = interval

    @property
    def ascending(self):
        return self, ORDER.asc
    
    @property
    def descending(self):
        return self, ORDER.desc
    
    @property
    def asc(self):
        return self, ORDER.asc
    
    @property
    def desc(self):
        return self, ORDER.desc

    def parse_n(self, n):
        if(isinstance(n, str)):
            return INTERVAL.parse_interval_str(n)
        elif(isinstance(n, int)):
            return n, self.unit
        elif(isinstance(n, tuple)):
            return n
        raise TypeError('n must be a str or a int not ' + type(n) + ' - ' + str(n) + '!')


time = __time_column__()