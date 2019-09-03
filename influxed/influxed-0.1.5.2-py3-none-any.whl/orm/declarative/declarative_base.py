#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: declarative_base.py
 File Created: Tuesday, 19th March 2019 10:48:51 am
 Author: ESR - Romeren (emilromer@hotmail.com)
 -----
 Copyright 2019 OpenSourced, OpenSourced
 -----
 Last Modified:
 Date	By	Comments
 -----
"""

from influxed.orm.measurement import Measurement

class DecarativeBase(object):
    """
    """
    __database__ = None
    __measurement__ = None


    @classmethod
    def set_database(cls, val):
        cls.database = val
        return cls