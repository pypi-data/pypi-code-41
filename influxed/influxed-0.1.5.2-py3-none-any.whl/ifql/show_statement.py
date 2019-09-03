#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: show_statement.py
 File Created: Wednesday, 13th February 2019 9:25:26 am
 Author: ESR - Romeren (emilromer@hotmail.com)
 -----
 Copyright 2019 OpenSourced, OpenSourced
 -----
 Last Modified:
 Date	By	Comments
 -----
"""
from influxed.ifql.exceptions import MissingArgument
from influxed.ifql.util import KEY_WORDS
from influxed.ifql.statement import CommonStatementFormatter


class ShowStatementBuilder(CommonStatementFormatter):

    def __init__(self, show_key_word=None, hook=None):
        super(ShowStatementBuilder, self).__init__(hook=hook)
        self._show_key_word = show_key_word
    
    @property
    def tag_keys(self):
        self._show_key_word = KEY_WORDS.TAG_KEYS
        return self
    
    @property
    def tag_values(self):
        self._show_key_word = KEY_WORDS.TAG_VALUES
        return self

    @property
    def field_keys(self):
        self._show_key_word = KEY_WORDS.FIELD_KEYS
        return self
    
    @property
    def measurements(self):
        self._show_key_word = KEY_WORDS.MEASUREMENTS
        return self
    
    @property
    def series(self):
        self._show_key_word = KEY_WORDS.SERIES
        return self

    @property
    def databases(self):
        self._show_key_word = KEY_WORDS.DATABASES
        return self

    @property
    def retention_policies(self):
        self._show_key_word = KEY_WORDS.RETENTION_POLICIES
        return self

    @property
    def users(self):
        self._show_key_word = KEY_WORDS.USERS
        return self

    def from_(self, measurement):
        self._measurement = measurement
        return self

    def _format(self):
        if(self._show_key_word is None):
            raise MissingArgument('Statement is missing SHOW_KEY_WORD! Supply it in costructor or by using property: tag_keys, tag_values, field_keys, measurements, series, databases, retention_policies or users')
        return self._format_show_query()
