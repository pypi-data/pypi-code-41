#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: select_statement.py
 File Created: Friday, 3rd May 2019 1:33:37 pm
 Author: ESR - Romeren (emilromer@hotmail.com)
 -----
 Copyright 2019 OpenSourced, OpenSourced
 -----
 Last Modified:
 Date	By	Comments
 -----
"""
from influxed.ifql.statement import CommonStatementFormatter, UsesFrom
from influxed.ifql.util import ORDER, OPERATOR, str_needs_escape
from influxed.ifql.column import time, Column, __time_column__
from influxed.ifql.filter import WhereFilter
from influxed.ifql.exceptions import MissingArgument
from influxed.ifql.functions import Expression, Func, Count, Sum, Max, Mean, Min, Median, Distinct, Percentile, Derivative, Stddev, First, Last, Difference

class SelectStatementBuilder(CommonStatementFormatter, UsesFrom):
    

    def __init__(self, *expressions, measurement=None, hook=None):
        super(SelectStatementBuilder, self).__init__(hook=hook)
        UsesFrom.__init__(self, isRequired=True)
        self._measurement = measurement
        if(expressions):
            self.select(*expressions)

    def select(self, *expressions):
        """
            Could be a one or more column names or expressions composed of
            functions from http://influxdb.org/docs/query_language/functions.html
        """
        if not expressions:
            raise TypeError("Select takes at least one expression")
        if(isinstance(self._select_expressions, tuple)):
            self._select_expressions = list(self._select_expressions)
        
        self._select_expressions.extend(list(expressions))
        return self
    
    def with_series(self, *expressions):
        """
            Could be a one or more column names or expressions composed of
            functions from http://influxdb.org/docs/query_language/functions.html
            
            Differs from select by overwriting the current selection with the new one.
            Operates like sqlalchemy with_entities
        """
        if not expressions:
            raise TypeError("Select takes at least one expression")
        self._select_expressions = expressions
        return self

    def add_to_filter(self, wherefilter, *clauses):
        for x in clauses:
            if(isinstance(x, OPERATOR)):
                subfilter = self.add_to_filter(WhereFilter(x), *x.call_arguments)
                wherefilter.sub_filters.append(subfilter)
            else:
                wherefilter.add(**x)
        return wherefilter

    def filter_by(self, **clauses):
        """
        .filter_by(something=something,
               something_else=something)
        See "The Where Clause" at http://influxdb.org/docs/query_language/
        OR operations are not supported
        TODO:
            support OR operations by adding in some kind of _Or function
            see http://docs.sqlalchemy.org/en/rel_0_9/orm/tutorial.html#common-filter-operators
        """
        for k,v in clauses.items():
            self.add_to_filter(self._where, dict(
                    field=k,
                    operator=self._default_operator,
                    value=v
                )
            )
        return self

    def filter(self, *clauses):
        """
        .filter(something==something,
               something_else==something)
        See "The Where Clause" at http://influxdb.org/docs/query_language/
        """
        self.add_to_filter(self._where, *clauses)
        return self

    def group_by(self, *expressions):
        if not expressions:
            raise TypeError("Select takes at least one expression")
        self._group_by.extend(expressions)
        return self

    def fill(self, value):
        """
            Fill empty values with value of expression 
        """
        self._fill = value
        return self

    def limit(self, n):
        if(n <= 0):
            raise ValueError('Limit must be a positive non zero value not ' + str(n))
        self._limit = n
        return self

    def order_by(self, field, order=ORDER.asc):
        """
            Allows you to order by time ascending or descending.
            Time is the only way to order from InfluxDB itself.
        """
        if(isinstance(field, tuple) and len(field) == 2):
            field, order = field
        if not isinstance(order, ORDER):
            raise ValueError("order must either be ORDER.ASC' or ORDER.DESC")
        self._order_by = [field]
        self._order = order
        return self

    def first(self, n=1):
        """
            Fetch the first n rows
            same as calling .limit(n).all()
        """
        return self.limit(n).all()
    
    def last(self, n=1):
        """
            Fetch the first n rows
            This function is similar to call order_by(time, desc).first(n)
        """
        return self.order_by(time, ORDER.desc).first(n)
    
    def distinct(self):
        """
            Applies Sum() function to all items in selection

            Handy for group_by statements
        """
        self._select_expressions = [Distinct(x) for x in self._select_expressions]
        return self

    def count(self):
        """
            Applies Sum() function to all items in selection

            Handy for group_by statements
        """
        self._select_expressions = [Count(x) for x in self._select_expressions]
        return self

    def sum(self):
        """
            Applies Sum() function to all items in selection

            Handy for group_by statements
        """
        self._select_expressions = [Sum(x) for x in self._select_expressions]
        return self

    def max(self):
        """
            Applies max() function to all items in selection

            Handy for group_by statements
        """
        self._select_expressions = [Max(x) for x in self._select_expressions]
        return self
    
    def min(self):
        """
            Applies Min() function to all items in selection

            Handy for group_by statements
        """
        self._select_expressions = [Min(x) for x in self._select_expressions]
        return self
    
    def mean(self):
        """
            Applies mean() function to all items in selection

            Handy for group_by statements
        """
        self._select_expressions = [Mean(x) for x in self._select_expressions]
        return self
    
    def median(self):
        """
            Applies mean() function to all items in selection

            Handy for group_by statements
        """
        self._select_expressions = [Median(x) for x in self._select_expressions]
        return self
    
    def percentile(self):
        """
            Applies percentile() function to all items in selection

            Handy for group_by statements
        """
        self._select_expressions = [Percentile(x) for x in self._select_expressions]
        return self
    
    def derivative(self):
        """
            Applies derivative() function to all items in selection

            Handy for group_by statements
        """
        self._select_expressions = [Derivative(x) for x in self._select_expressions]
        return self
    
    def difference(self):
        """
            Applies difference() function to all items in selection

            Handy for group_by statements
        """
        self._select_expressions = [Difference(x) for x in self._select_expressions]
        return self
    

    def std(self):
        """
            Applies std() function to all items in selection

            Handy for group_by statements
        """
        self._select_expressions = [Stddev(x) for x in self._select_expressions]
        return self

    def apply_first(self):
        """
            Applies First() function to all items in selection

            Handy for group_by statements
        """
        self._select_expressions = [First(x) for x in self._select_expressions]
        return self

    def apply_last(self):
        """
            Applies Last() function to all items in selection

            Handy for group_by statements
        """
        self._select_expressions = [Last(x) for x in self._select_expressions]
        return self

    def _format(self):
        return self._format_select_query()

    def _format_select_expression(self, expr):
        """
            Format a single select expression
        """
        formatted = expr
        if issubclass(type(expr), (Expression, Func, Column)):
            formatted = expr.format()
        else:
            if(str_needs_escape(formatted)):
                formatted = '"' + formatted + '"'
        return formatted

    def _format_select_expressions(self, select_expressions):
        """
            Format the function stack to form a function clause
            If it's empty and there are no functions we just return the column name
        """
        if(not select_expressions):
            return '*'
        return ", ".join([
            self._format_select_expression(s) for s in select_expressions
        ])

    def _format_select(self):
        return "SELECT " + self._format_select_expressions(self._select_expressions)

    def _format_into(self):
        if self._into_series:
            return 'INTO %s' % self._into_series
        return ''

    def _format_group_by(self):
        if self._group_by:
            group_by_strs = [s for s in self._group_by if isinstance(s, str)]
            for i in range(len(group_by_strs)):
                if(str_needs_escape(group_by_strs[i])):
                    group_by_strs[i] = '"' + group_by_strs[i] + '"'
            group_by_col = [s for s in self._group_by if issubclass(type(s), Column)]
            time_col = [s for s in group_by_col if isinstance(s, __time_column__)]

            group_by_strs += [c.format() for c in group_by_col]
            invalid_select = next(filter(lambda x: not isinstance(x, str) and not issubclass(type(x), Func), self._select_expressions), None)
            if(invalid_select and len(time_col) > 0):
                raise MissingArgument('Column ' + invalid_select + ' does not have a aggregation function!')
            
            return 'GROUP BY ' + ", ".join(group_by_strs)
        return ''

    def _format_order(self):
        clause = ''
        if self._order:
            order_by_strs = [s for s in self._order_by if isinstance(s, str)]
            order_by_col = [s for s in self._order_by if isinstance(s, Column)]
            order_by_strs += [c.name for c in order_by_col]
            clause = "ORDER BY " + ' '.join(order_by_strs) + " " + self._order._value_
        return clause

    def _format_limit(self):
        clause = ''
        if self._limit:
            clause = "LIMIT %i" % self._limit
        return clause

    def _format_fill(self):
        clause = ''
        if(self._fill is not None):
            clause = 'FILL(' + str(self._fill) + ')'
        return clause

    def _format_select_query(self):
        query = ' '.join([ x for x in [
                self._format_select(),
                self._format_from(),
                self._format_where(),
                self._format_group_by(),
                self._format_fill(),
                self._format_into(),
                self._format_order(),
                self._format_limit()
            ] if x]
        )
        return query

    def __str__(self):
        return self._format()
