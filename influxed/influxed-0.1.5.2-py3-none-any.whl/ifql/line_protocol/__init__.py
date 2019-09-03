#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: __init__.py
 File Created: Wednesday, 23rd January 2019 3:39:03 pm
 Author: ESR - Romeren (emilromer@hotmail.com)
 -----
 Copyright 2019 OpenSourced, OpenSourced
 -----
 Last Modified:
 Date	By	Comments
 -----
"""
name = "influxed.ifql.line_protocol"
try:
    import pandas as pd
    from influxed.ifql.line_protocol.dataframe_to_line import to_lines as df_to_lines
    from influxed.ifql.line_protocol.series_to_line import to_lines as se_to_lines
except ImportError as e:
    pd = None
    df_to_lines = None
    se_to_lines = None

from influxed.ifql.line_protocol.dict_to_line import to_lines as dict_to_lines
from influxed.ifql.line_protocol.list_to_line import to_lines as list_to_lines



def to_lines(value, measurement):
    if(pd and isinstance(value, pd.DataFrame)):
        return df_to_lines(value, measurement)
    elif(pd and isinstance(value, pd.Series)):
        return se_to_lines(value, measurement)
    elif(isinstance(value, list)):
        return list_to_lines(value, measurement)
    elif(isinstance(value, dict)):
        return dict_to_lines(value, measurement)
    raise ValueError('Unsupported value type '+type(value))