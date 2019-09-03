#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: __init__.py
 File Created: Wednesday, 20th February 2019 7:39:36 pm
 Author: ESR - Romeren (emilromer@hotmail.com)
 -----
 Copyright 2019 OpenSourced, OpenSourced
 -----
 Last Modified:
 Date	By	Comments
 -----
"""
name = "influxed.ifql"
from influxed.ifql.select_statement import SelectStatementBuilder as select
from influxed.ifql.show_statement import ShowStatementBuilder as show
from influxed.ifql.create_statement import create_statement as create
from influxed.ifql.grant_statement import GrantStatementBuilder as grant
from influxed.ifql.revoke_statement import RevokeStatementBuilder as revoke
from influxed.ifql.insert_statement import InsertStatementBuilder as insert


from influxed.ifql.util import OPERATOR as OPERATORS
from influxed.ifql.util import KEY_WORDS
from influxed.ifql.column import Field, Tag
from influxed.ifql.column import time
from influxed.ifql.infix_operators import like, nlike