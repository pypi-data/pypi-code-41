#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: revoke_statement.py
 File Created: Friday, 26th July 2019 3:33:08 pm
 Author: ESR - Romeren (emil@spectral.energy)
 -----
 Copyright 2019 Spectral, Spectral
 -----
 Last Modified:
 Date	By	Comments
 -----
"""

from influxed.ifql.statement import CommonStatementFormatter
from influxed.ifql.exceptions import MissingArgument
from influxed.ifql.util import PRIVILEGES


class RevokeStatementBuilder(CommonStatementFormatter):
    """
        REVOKE [READ,WRITE,ALL] ON <database_name> FROM <username>
    """

    def __init__(self, previleges, hook=None):
        super(RevokeStatementBuilder, self).__init__(self, hook=hook)
        self.__previleges__ = previleges

    def from_(self, username):
        self.username = username
        return self 

    def on(self, database):
        self.__database__ = database
        return self

    def format_from(self):
        return 'FROM '+self.username

    def format_on(self):
        return 'ON '+self.__database__

    def format_previleges(self):
        if(isinstance(self.__previleges__, PRIVILEGES)):
            return self.__previleges__.value.split(' ')[0]
        return self.__previleges__.split(' ')[0]

    def format_to(self):
        if(not self.username):
            raise MissingArgument('Missing argument username!')
        return 'TO '+self.username

    def format(self):
        return 'REVOKE '+self.format_previleges()+' '+self.format_on()+' '+self.format_to()