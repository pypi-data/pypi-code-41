#!/usr/bin/env python

'''
Usage:
    pgmeta --target <alias> --database <db> <schema> --table <table>
    pgmeta --target <alias> --database <db> <schema> --tables <tables>...
    pgmeta --target <alias> --database <db> <schema> --tables --match=<regex>
    pgmeta --targets

'''


import os, sys
import re
import json
from pathlib import Path
from collections import namedtuple
from contextlib import contextmanager
import docopt
import sqlalchemy as sqla
from sqlalchemy.sql import text
from snap import common

URL_TEMPLATE = '{db_type}://{user}:{passwd}@{host}:{port}/{database}'

METADATA_QUERY_TEMPLATE = """
SELECT table_name, column_name, udt_name, character_maximum_length 
FROM information_schema.columns
WHERE table_schema = '{schema}'
AND table_name  = '{table}'
"""

TABLE_LIST_QUERY_TEMPLATE = """
SELECT table_name 
FROM information_schema.tables
WHERE table_schema = '{schema}'
AND table_type = 'BASE TABLE'
"""

TargetConfig = namedtuple('TargetConfig', 'host port user password')

class ConfigDirNotFound(Exception):
    def __init__(self):
        pass

@contextmanager
def db_connect(**kwargs):
    db_url = URL_TEMPLATE.format(**kwargs)
    engine = sqla.create_engine(db_url, echo=False)
    print('### Connected to PostgreSQL DB.', file=sys.stderr)
    yield engine.connect()

                
def load_targets():
    targets = {}
    config_dir = os.getenv('PGX_CFG') or os.path.join(str(Path.home()), '.pgx')
    if not os.path.isdir(config_dir):
        raise ConfigDirNotFound()
    
    configfile = os.path.join(config_dir, 'config.yaml')
    yaml_config = common.read_config_file(configfile)
    
    for name in yaml_config['targets']:
        hostname = yaml_config['targets'][name]['host']
        port = int(yaml_config['targets'][name]['port'])
        user = yaml_config['targets'][name]['user']
        password = None
        if yaml_config['targets'][name].get('password'):
            password = common.load_config_var(yaml_config['targets'][name]['password'])
        targets[name] = TargetConfig(host=hostname, port=port, user=user, password=password)
    return targets


def load_matching_tablenames(schema, tablename_regex, db_connection):
    query = TABLE_LIST_QUERY_TEMPLATE.format(schema=schema)
    statement = text(query)
    results = db_connection.execute(statement)
    tablenames = []
    for record in results:
        if tablename_regex.match(record['table_name']):
            tablenames.append(record['table_name'])
    return tablenames


def resolve_type(column_type, column_record):
    type_suffix = ''
    if column_record['character_maximum_length'] is not None:
        type_suffix = '(%s)' % column_record['character_maximum_length']

    return '%s%s' % (column_type, type_suffix)



def generate_metadata_from_query_results(results, table, schema):
    table_metadata = {}
    table_metadata['table_name'] = table
    table_metadata['columns'] = []
    for record in results:
        table_metadata['columns'].append({
            'column_name': record['column_name'],
            'column_type': resolve_type(record['udt_name'], record)
        })
    
    return table_metadata


def main(args):
    #print(common.jsonpretty(args))
    target_db = args['<db>']
    target_schema = args['<schema>']

    db_targets = load_targets()

    if args['--targets']:
        # list targets
        for alias, raw_target in db_targets.items():
            target = raw_target._asdict()
            target['password'] = '*************'

            record = {
                alias: target
            }
            print(json.dumps(record))
        return

    target = db_targets.get(args['<alias>'])
    if not target:
        raise Exception('no database target registered in config.yaml under the alias %s.' % args['<alias>'])

    metadata = {}
    metadata['schema_name'] = target_schema
    metadata['tables'] = []

    with db_connect(db_type='postgresql+psycopg2',
                        user=target.user,
                        passwd=target.password,
                        host=target.host,
                        port=target.port,
                        database=target_db) as connection:

        if args['--table']:            
            query = METADATA_QUERY_TEMPLATE.format(
                schema=target_schema,
                table=args['<table>']
            )
            statement = text(query)
            results = connection.execute(statement)
            metadata['tables'].append(generate_metadata_from_query_results(results, args['<table>'], target_schema))

        elif args['--tables']:
            if args['--match']:                
                regex_string = args['--match']
                if regex_string == '*':
                    regex_string = ''
                tablename_rx = re.compile(regex_string)
                table_list = load_matching_tablenames(target_schema, tablename_rx, connection)
            else:            
                table_list = [tbl.lstrip().rstrip() for tbl in args['<tables>'][0].split(',')]
                
            for table in table_list:
                query = METADATA_QUERY_TEMPLATE.format(
                    schema=target_schema,
                    table=table
                )
                statement = text(query)
                results = connection.execute(statement)
                metadata['tables'].append(generate_metadata_from_query_results(results, table, target_schema))

    print(json.dumps(metadata))

if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    main(args)