#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: functions.py
 File Created: Thursday, 11th April 2019 6:58:29 pm
 Author: ESR - Romeren (emilromer@hotmail.com)
 -----
 Copyright 2019 OpenSourced, OpenSourced
 -----
 Last Modified:
 Date	By	Comments
 -----
"""
from influxed.ifql.util import str_needs_escape, ARITMATIC_OPERATOR

class Expression(object):
    def __init__(self, expression):
        self._expression = expression
        self._as = ''

    def as_(self, alias):
        self._as = alias
        return self

    def _format_as(self):
        return "%s" % " AS %s" % (self._as) if self._as else ''


    def __add__(self, other):
        return Algebraic(self, ARITMATIC_OPERATOR.add, other)

    def __radd__(self, other):
        return Algebraic(other, ARITMATIC_OPERATOR.add, self)

    def __sub__(self, other):
        return Algebraic(self, ARITMATIC_OPERATOR.subtract, other)

    def __rsub__(self, other):
        return Algebraic(other, ARITMATIC_OPERATOR.subtract, self)

    def __mul__(self, other):
        return Algebraic(self, ARITMATIC_OPERATOR.multiply, other)

    def __rmul__(self, other):
        return Algebraic(other, ARITMATIC_OPERATOR.multiply, self)

    def __truediv__(self, other):
        return Algebraic(self, ARITMATIC_OPERATOR.devide, other)

    def __rtruediv__(self, other):
        return Algebraic(other, ARITMATIC_OPERATOR.devide, self)



    def format(self):
        if isinstance(self._expression, Expression):
            formatted = "(%s)" % self._expression.format()
        formatted = "%s" % self._expression
        return "%s%s" % (formatted, self._format_as())

class Algebraic(Expression):

    def __init__(self, left, operator, right):
        super(Algebraic, self).__init__(None)
        self.left = left
        self.right = right
        self.operator = operator
    
    def format_variable(self, variable):
        if(isinstance(variable, (int, float))):
            return str(variable)
        elif(isinstance(variable, Algebraic)):
            return "(" + variable.format() + ")"
        else:
            return variable.format()

    def format_operator(self, operator):
        if(isinstance(operator, str)):
            return operator
        else:
            return operator.value

    def format(self):
        formatted_left = self.format_variable(self.left)
        formatted_right = self.format_variable(self.right)
        formatted_operator = self.format_operator(self.operator)
        return formatted_left + " " + formatted_operator + " " + formatted_right


class Func(Expression):
    """Base class for an InfluxDB function
    """
    identifier = None
    _valid_arg_types = {str}

    def __init__(self, *args):
        super(Func, self).__init__(None)
        self.validate_args(*args)
        self._args = args

    def validate_arg_length(self, args, length):
        if len(args) != length:
            raise ValueError(u"Function %s takes %i arguments" % (
                self.identifier, length))

    def validate_args(self, *args):
        self.validate_arg_length(args, 1)

    def format(self):
        formatted_args = []
        for arg in self._args:
            if issubclass(type(arg), Func):
                formatted_args.append(arg.format())
            elif type(arg) in self._valid_arg_types:
                if(str_needs_escape(arg)):
                    formatted_args.append('"' + arg + '"')
                else:
                    formatted_args.append(str(arg))
            else:
                formatted_args.append(u'%s' % arg.format())
        formatted = u"%s(%s)%s" % (self.identifier, ", ".join(formatted_args), self._format_as())
        return formatted


class Count(Func):
    identifier = 'COUNT'


class Min(Func):
    identifier = 'MIN'


class Max(Func):
    identifier = 'MAX'


class Mean(Func):
    identifier = 'MEAN'


class Median(Func):
    identifier = 'MEDIAN'


class Distinct(Func):
    identifier = 'DISTINCT'


class Percentile(Func):
    identifier = 'PERCENTILE'
    _valid_first_arg_types = {int, float}

    def validate_args(self, *args):
        self.validate_arg_length(args, 2)
        if type(args[1]) not in self._valid_first_arg_types:
            raise TypeError(
                "Second argument to %s must be int or float" % self.identifier)
        if args[1] <= 0 or args[1] >= 100.0:
            raise ValueError(
                "Second argument to %s must be between 0 and 100" % self.identifier)


class Derivative(Func):
    identifier = 'DERIVATIVE'


class Difference(Func):
    identifier = 'DIFFERENCE'


class Sum(Func):
    identifier = 'SUM'


class Stddev(Func):
    identifier = 'STDDEV'


class First(Func):
    identifier = 'FIRST'


class Last(Func):
    identifier = 'LAST'

