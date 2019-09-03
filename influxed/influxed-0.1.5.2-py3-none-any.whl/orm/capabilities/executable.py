#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: executable.py
 File Created: Thursday, 2nd May 2019 4:18:26 pm
 Author: ESR - Romeren (emil@spectral.energy)
 -----
 Copyright 2019 Spectral, Spectral
 -----
 Last Modified:
 Date	By	Comments
 -----
"""


class Executable(object):

    @property
    def mediator(self):
        return self.__mediator__

    @property
    def connection_string(self):
        return self.__connection_string__

    @property
    def username(self):
        return self.__username__

    def execute(self, query):
        return self.mediator.execute(query, connection_string=self.connection_string, username=self.username)
