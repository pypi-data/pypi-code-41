#!/usr/bin/env python

import sys
from collections import namedtuple, OrderedDict
from snap import snap, common
from google.cloud import bigquery


ReportInputField = namedtuple('ReportInputField', 'name input_class')
ReportConnectionTarget = namedtuple('ReportConnectionTarget', 'name connector_func')


class FilterPredicateLike(object):
    def __init__(self, field_name, value):
        self.field_name = field_name        
        self.value = value

    def sql(self):
        return "{field} LIKE '{value}'".format(field=self.field_name,
                                               value=self.value)


class Or(object):
    def __init__(self, *filter_predicates):
        self.predicates = filter_predicates

    def sql(self):
        return ' OR\n'.join([p.sql() for p in self.predicates])


class And(object):
    def __init__(self, *fillter_predicates):
        self.predicates = fillter_predicates

    def sql(self):
        return ' AND\n'.join([p.sql() for p in self.predicates])


class ReportQuerySpec(object):
    def __init__(self, template_string, *inputs, **kwargs):
        self.inputs = [i for i in inputs] # array of ReportInputFields
        self.sql_template = template_string


    def pre_render(self, **kwargs):
        '''Override in subclass'''
        result = {}
        for key, value in kwargs.items():
            result[key] = value
        return result


    def render(self, **kwargs):
        inputs = self.pre_render(**kwargs)
        input_names = [key for key in inputs.keys()]
        kwreader = common.KeywordArgReader(*[i.name for i in self.inputs])
        kwreader.read(**inputs)
        return self.sql_template.format(**kwargs)



class ReportingEngine(object):
    def __init__(self):
        self._query_specs = OrderedDict()
        self.connectors = {}

    def has_report_alias(self, report_name):
        return self._query_specs.get(report_name) is not None


    def add_report(self, report_query_spec, alias):
        self._query_specs[alias] = report_query_spec


    def connect_reports(self, report_a_name, report_b_name, connector_func):
        if not self.has_report_alias(report_a_name):
            raise Exception('No report registered under alias "%s".' % report_a_name)
        
        if not self.has_report_alias(report_b_name):
                raise Exception('No report registered under alias "%s".' % report_b_name)

        self.connectors[report_a_name] = ReportConnectionTarget(name=report_b_name,
                                                                connector_func=connector_func)


    @property
    def reports(self):
        return self._query_specs.keys()


    def exec_query(self, query_string, **kwargs):
        '''implement in subclass'''
        return {}


    def run(self, report_name, **kwargs):
        qspec = self._query_specs.get(report_name)
        if not qspec:
            raise Exception('No query spec registered under the alias %s.' % report_name)

        sql_query = qspec.render(**kwargs)
        if kwargs.get('debug'):
            print('### Executing report "%s":' % (report_name), file=sys.stderr)
            print(sql_query, file=sys.stderr)

        return self.exec_query(sql_query, **kwargs)


    def run_sequence(self, initial_report_name, **kwargs):
        pass
        '''
        sql_query = component.render(**report_input)
        if kwargs.get('debug'):
            print(sql_query)
        resultset = self.exec_query(sql_query, **report_input)
        num_reports_run += 1
        if num_reports_run < component_count:
            report_input.update(resultset)
                    
        return resultset
        '''
            

class BigQueryReportingEngine(ReportingEngine):
    def __init__(self):
        super().__init__()
        self.client = bigquery.Client()


    def exec_query(self, query_string, **kwargs):
        query_job = self.client.query(query_string)
        resultset = query_job.result()
        data = []
        for row in resultset:
            rowdata = {}
            for key, value in row.items():
                rowdata[key] = value
            data.append(rowdata)
        return data



        
