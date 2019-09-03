#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: util.py
 File Created: Thursday, 21st February 2019 10:17:35 pm
 Author: ESR - Romeren (emilromer@hotmail.com)
 -----
 Copyright 2019 OpenSourced, OpenSourced
 -----
 Last Modified:
 Date	By	Comments
 -----
"""
import re
from enum import Enum

escape_str_regex = re.compile('[0-9].*|.*([^A-z,0-9,_]).*|(ALL|ALTER|ANALYZE|ANY|AS|ASC|BEGIN|BY|CREATE|CONTINUOUS|DATABASE|DATABASES|DEFAULT|DELETE|DESC|DESTINATIONS|DIAGNOSTICS|DISTINCT|DROP|DURATION|END|EVERY|EXPLAIN|FIELD|FOR|FROM|GRANT|GRANTS|GROUP|GROUPS|IN|INF|INSERT|INTO|KEY|KEYS|KILL|LIMIT|SHOW|MEASUREMENT|MEASUREMENTS|NAME|OFFSET|ON|ORDER|PASSWORD|POLICY|POLICIES|PRIVILEGES|QUERIES|QUERY|READ|REPLICATION|RESAMPLE|RETENTION|REVOKE|SELECT|SERIES|SET|SHARD|SHARDS|SLIMIT|SOFFSET|STATS|SUBSCRIPTION|SUBSCRIPTIONS|TAG|TO|USER|USERS|VALUES|WHERE|WITH|WRITE)', re.I)


def str_needs_escape(string):
    if(escape_str_regex.fullmatch(string) and string[0] + string[-1] != '""'):
        return True
    return False

class ORDER(Enum):
    asc = 'ASC'
    desc = 'DESC'

class COMPARISON_OPERATOR(Enum):
    eq = '='
    neq = '!='
    gt = '>'
    gteq = '>='
    lt = '<'
    lteq = '<='
    regexMatch = '=~'
    regexNotMatch = '!~'

class ARITMATIC_OPERATOR(Enum):
    add = "+"
    subtract = "-"
    devide = "/"
    multiply = "*"


class INTERVAL(Enum):
    week = 'w'
    day = 'd'
    hour = 'h'
    minute = 'm'
    sec = 's'
    milisec = 'ms'
    microsec ='u'
    nanosec = 'ns'

    @property
    def factor(self):
        if(hasattr(self, '__n__')):
            return self.__n__
        return 1

    def n(self, val):
        if(isinstance(val, int) and val > 0):
            self.__n__ = val
            return self
        raise ValueError('Interval factor must be a positive integer, not ' + val)

    def format(self):
        return str(self.factor) + str(self.value)

    def __str__(self):
        return self.format()

    @staticmethod
    def parse_interval_str(string):
        unit = INTERVAL.get_unit_from_string(string)

        val = int(string[0:len(unit)])
        return INTERVAL(unit).n(val)
    
    @staticmethod
    def get_unit_from_string(string):
        available_letters = ['w', 'd', 'h', 'm', 's', 'u', 'ns', 'ms']
        last = string[-1]

        if(last == 's' and string[-2] + last in available_letters):
                last = string[-2] + last
        
        if(last not in available_letters):
            raise ValueError('Interval str "' + string + '" is not valid')
        
        return last


class OPERATOR(Enum):
    and_= 'AND'
    or_ = 'OR'

    def __call__(self, *args):
        self.call_arguments = args
        return self

class KEY_WORDS(Enum):
    TAG_KEYS = 'TAG KEYS'
    TAG_VALUES = 'TAG VALUES'
    FIELD_KEYS = 'FIELD KEYS'
    MEASUREMENTS = 'MEASUREMENTS'
    SERIES = 'SERIES'
    DATABASES = 'DATABASES'
    RETENTION_POLICIES = 'RETENTION POLICIES'
    USERS = 'USERS'
    

class PRIVILEGES(Enum):
    READ = 'READ PRIVILEGES'
    WRITE = 'WRITE PRIVILEGES'
    ALL = 'ALL PRIVILEGES'