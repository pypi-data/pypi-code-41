#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: infix_operators.py
 File Created: Tuesday, 3rd September 2019 2:16:12 pm
 Author: ESR - Romeren (emil@spectral.energy)
 -----
 Copyright 2019 Spectral, Spectral
 -----
 Last Modified:
 Date	By	Comments
 -----
"""
from influxed.ifql.util import COMPARISON_OPERATOR
from influxed.ifql.functions import Algebraic

class Infix:
    def __init__(self, function):
        self.function = function
    def __ror__(self, other):
        return Infix(lambda x, self=self, other=other: self.function(other, x))
    def __or__(self, other):
        return self.function(other)
    def __rlshift__(self, other):
        return Infix(lambda x, self=self, other=other: self.function(other, x))
    def __rshift__(self, other):
        return self.function(other)
    def __call__(self, value1, value2):
        return self.function(value1, value2)


def like_func(x, y):
    return Algebraic(x, COMPARISON_OPERATOR.regexMatch, y)

def not_like_func(x, y):
    return Algebraic(x, COMPARISON_OPERATOR.regexNotMatch, y)

like = Infix(like_func)
nlike = Infix(not_like_func)