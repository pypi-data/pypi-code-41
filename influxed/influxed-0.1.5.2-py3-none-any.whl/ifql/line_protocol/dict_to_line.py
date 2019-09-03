#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: dict_to_line.py
 File Created: Monday, 12th August 2019 5:06:48 pm
 Author: ESR - Romeren (emil@spectral.energy)
 -----
 Copyright 2019 Spectral, Spectral
 -----
 Last Modified:
 Date	By	Comments
 -----
"""

import datetime as dt
import math


def to_lines(dict_, measurement):
    """
        Format a python dict into line protocol.

        Dict should contain key "time" for the influx db
    """
    return [dict_to_line_protocol(dict_, measurement)]


def dict_to_line_protocol(dict_, measurement):
    """
        Format a python dict into line protocol.

        Dict should contain key "time" for the influx db
    """
    tags = []
    fields = []
    time = dict_.pop('time', None)
    
    if(time is None):
        time = dt.datetime.now()
    
    if(isinstance(time, dt.datetime)):
        time = str(int(time.timestamp() *10e8))
    elif(isinstance(time, float)):
        time = str(int(time))

    if(not isinstance(time, (int, str))):
        raise Exception("'time' key in dict is not int or float", dict_)
    
    for k, v in dict_.items():

        if(isinstance(v, str)):
            tags.append(format_key(k, v))
        elif(isinstance(v, float) and math.isnan(v)):
            continue
        elif(isinstance(v, (int, float))):
            fields.append(format_number(k, v))
        elif(v is None):
            continue
        else:
            raise Exception("Tag- or Field-value is neither string, int or float", (k, v))
    if(len(fields) < 1):
        return None
    tags = ','.join(tags)
    fields = ','.join(fields)
    
    return dict_to_line_protocol_to_line(measurement, tags, fields, time)

def format_key(k, v, escape=True):
    """
        Format a key and value for line-protocol
    """
    if(escape and isinstance(v, str)):
        v = v.replace('\\', r'\\\\').replace(' ', r'\ ').replace(',', r'\,').replace('=', r'\=')
    format_str = '{key}={value}'
    return format_str.format(
        key=k.replace(' ', '').replace('.', '').replace('/', '').replace('\\', ''),
        value=v
    )

def format_number(k, v):
    return format_key(k, '{:.5f}'.format(v), escape=False)

def dict_to_line_protocol_to_line(measurement, tag_set, field_set, timestamp):
    """
        Format a observation to a line-protocol item
    """
    if(tag_set != ""):
        tag_set = ',' + tag_set
    return "{measurement}{tag_set} {field_set} {timestamp}".format(
        measurement=measurement,
        tag_set=tag_set,
        field_set=field_set,
        timestamp=timestamp
    )