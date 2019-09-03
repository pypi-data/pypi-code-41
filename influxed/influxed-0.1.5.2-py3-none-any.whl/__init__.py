#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: __init__.py
 File Created: Wednesday, 20th February 2019 7:39:38 pm
 Author: ESR - Romeren (emilromer@hotmail.com)
 -----
 Copyright 2019 OpenSourced, OpenSourced
 -----
 Last Modified:
 Date	By	Comments
 -----
"""
name = "influxed"
from influxed.ifql import select
from influxed.ifql import show
from influxed.ifql import create
from influxed.ifql import grant
from influxed.ifql import revoke
from influxed.ifql import insert

from influxed.ifql import OPERATORS, KEY_WORDS
from influxed.ifql import Field, Tag
from influxed.ifql import time

from influxed.ifql import like, nlike

from influxed.orm import engine