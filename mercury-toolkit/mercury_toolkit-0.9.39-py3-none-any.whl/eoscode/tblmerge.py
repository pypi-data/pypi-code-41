#!/usr/bin/env python

'''
Usage:
    tblmerge --config <configfile> --dataset <dataset_name> [--filter_values <filter_values_filename>][--limit=<limit>]
'''

import os, sys
import json
from collections import namedtuple
from snap import common
import docopt


class TableSpec(object):
    def __init__(self, schema, tablename, id_column, alias=None, **kwargs):
        self.schema = schema
        self.name = tablename
        self.alias = alias if alias else tablename
        self.columns = []
        self.id_column = id_column

    def add_column(self, name):
        self.columns.append(name)


FilterSpec = namedtuple('FilterSpec', 'tablename fieldname')

MERGE_QUERY_TEMPLATE = """
SELECT DISTINCT p.patientbestrecordid,
{field_list_clause}
{from_clause}
{join_segment}
{filter_clause}
{limit_clause}
"""

TOP_500_QUERY_TEMPLATE = """
SELECT DISTINCT TOP 500 chai_patient_id
FROM ( 
    SELECT DISTINCT TOP 9999999999 chai_patient_id, NEWID()
    AS r 
    FROM qdm_v16.diagnosisactive
    WHERE lower(DiagnosisCode_Code) IN 
    ()
)

"""


def generate_field_list_clause(*tablespecs):
    field_designators = []
    for tablespec in tablespecs:
        for column_name in tablespec.columns:
            field_designators.append('{name}.{field} AS {name}_{field}'.format(name=tablespec.alias, field=column_name))

    return ', '.join(field_designators)


def generate_from_clause(core_tablespec):
    clause = 'FROM {schema}.{tablename} {alias}'
    return clause.format(schema=core_tablespec.schema,
                         tablename=core_tablespec.name,
                         alias=core_tablespec.alias)


def generate_join_clause(parent_tablespec, child_tablespec):
    clause = '''
    JOIN {child_table_schema}.{child_table_name} {child_table_alias}
    ON {parent_table_alias}.{id_field} = {child_table_alias}.{foreign_key}'''

    return clause.format(child_table_name=child_tablespec.name,
                         child_table_schema=child_tablespec.schema,
                         parent_table_alias=parent_tablespec.alias,                         
                         id_field=parent_tablespec.id_column,
                         child_table_alias=child_tablespec.alias,
                         foreign_key=child_tablespec.id_column)


def generate_filter_clause(filterspec, value_list):

    clause = '''
    WHERE
    {parent_table_alias}.{parent_table_field} IN
    ({values})
    '''

    return clause.format(parent_table_alias=filterspec.tablename,
                         parent_table_field=filterspec.fieldname,
                         values=', '.join(["'%s'" % value.lower() for value in value_list]))


def load_table_specs(datset_name, yaml_config):
    specs = []

    if not yaml_config['datasets'].get(datset_name):
        raise Exception('No dataset "%s" registered in config file.' % datset_name)

    dataset_config = yaml_config['datasets'][datset_name]

    schema = dataset_config['schema']
    id_column_name = dataset_config['id_column']

    for table_config in yaml_config['datasets'][datset_name]['tables']:
        tablename = None
        for key in table_config.keys():
            tablename = key
        configdata = table_config[tablename]
        alias = configdata.get('alias')
        tblspec = TableSpec(schema, tablename, id_column_name, alias)
        for column_name in configdata.get('columns', []):
            tblspec.add_column(column_name)

        specs.append(tblspec)

    return specs
 
def load_filter_values(filename):
    values = []
    with open(filename) as f:
        for line in f:
            values.append(line.lstrip().rstrip())
    return values


def main(args):
    configfile = args['<configfile>']
    yaml_config = common.read_config_file(configfile)
    dataset = args['<dataset_name>']

    filter_values = []
    if args['--filter_values'] == True:
        filter_values = load_filter_values(args['<filter_values_filename>'])

    specs = load_table_specs(dataset, yaml_config)    
    join_clauses = []
    parent_table_spec = specs[0]
    for tspec in specs[1:]:
        clause = generate_join_clause(parent_table_spec, tspec)
        join_clauses.append(clause)
        parent_table_spec = tspec

    fields = generate_field_list_clause(*specs)
    from_clause = generate_from_clause(specs[0])
    join_segment = '\n'.join(join_clauses)

    filterparam = FilterSpec(tablename='da', fieldname='DiagnosisCode_Code')
    filter_clause = generate_filter_clause(filterparam, filter_values)

    limit_clause = ''
    if args['--limit'] is not None:
        limit = int(args['--limit'])
        limit_clause = 'LIMIT %s' % limit

    print(MERGE_QUERY_TEMPLATE.format(field_list_clause=fields,
                                      from_clause=from_clause,
                                      join_segment=join_segment,
                                      filter_clause=filter_clause,
                                      limit_clause=limit_clause))


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    main(args)


'''
How to represent model state?
Fully accessible to applications involved
Discoverable via job ID when model is part of a pipeline run?
WHo gets to access it? 

Concurrent access to model state? Contend to make changes?

Local, file-based state mgmt (manager process)
ModelStateManager (network service) -- also file-based
Redis

                                            
HTTP service in front of S3 bucket as first cut?

priority 1: job management service
priority 2: model data management

'''