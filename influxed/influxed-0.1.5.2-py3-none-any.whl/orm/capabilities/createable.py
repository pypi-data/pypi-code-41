#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: createable.py
 File Created: Friday, 26th July 2019 3:46:33 pm
 Author: ESR - Romeren (emil@spectral.energy)
 -----
 Copyright 2019 Spectral, Spectral
 -----
 Last Modified:
 Date	By	Comments
 -----
"""

from influxed.orm.capabilities.executable import Executable
from influxed.ifql import create


class Creatable(Executable):
    """
        Definition of a object that can initiate a show query
    """
    def create(self, keyword):
        """
            Function for initiating a create query
        """
        return create(keyword, hook=self)
