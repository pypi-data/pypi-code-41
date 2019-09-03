#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: grant_statement.py
 File Created: Thursday, 21st February 2019 10:47:38 pm
 Author: ESR - Romeren (emilromer@hotmail.com)
 -----
 Copyright 2019 OpenSourced, OpenSourced
 -----
 Last Modified:
 Date	By	Comments
 -----
"""

from influxed.ifql.statement import CommonStatementFormatter
from influxed.ifql.util import PRIVILEGES
from influxed.ifql.exceptions import MissingArgument

class GrantStatementBuilder(CommonStatementFormatter):
    """
        GRANT ALL PRIVILEGES TO <username>
        GRANT [READ,WRITE,ALL] ON <database_name> TO <username>
    """

    def __init__(self, previleges=None, hook=None):
        super(GrantStatementBuilder, self).__init__(hook=hook)
        self.__previleges__ = previleges
        self.__database__ = None
        self.username = None

    @property
    def all(self):
        self.__previleges__ = PRIVILEGES.ALL
        return self
    
    @property
    def write(self):
        self.__previleges__ = PRIVILEGES.WRITE
        return self

    @property
    def read(self):
        self.__previleges__ = PRIVILEGES.READ
        return self

    def to(self, username):
        self.username = username
        return self 

    def on(self, database):
        self.__database__ = database
        return self

    def format_to(self):
        if(not self.username):
            raise MissingArgument('Missing argument username!')
        return 'TO ' + self.username

    def format_on(self):
        return 'ON ' + self.__database__

    def format_previleges(self, right_only=False):
        if(isinstance(self.__previleges__, PRIVILEGES)):
            return self.__previleges__.value if not right_only else self.__previleges__.value.split(' ')[0]
        return self.__previleges__ if not right_only else self.__previleges__.split(' ')[0]

    def format(self):
        if(self.__database__):
            return 'GRANT ' + self.format_previleges(True)+" "+self.format_on()+" "+self.format_to()
        return 'GRANT '+self.format_previleges()+' '+self.format_to()