#!/usr/bin/python

import uuid
import os, sys
import json
from snap import common
from mercury.dataload import DataStore
from sqlalchemy.sql import text
from collections import namedtuple

'''
with redshift_svc.connect() as cxn:
    tx = cxn.begin()
    print('### loading records to table %s from S3 object %s...' % (table_name, s3_key.uri))
    rs3ctx.import_records(cxn,
                            table_name,
                            s3_key,
                            'json')
    tx.commit()
'''

class FileStore(DataStore):
    def __init__(self, service_object_registry, *channels, **kwargs):
        DataStore.__init__(self, service_object_registry, *channels, **kwargs)
        kwreader = common.KeywordArgReader('filename')
        kwreader.read(**kwargs)
        self.filename = kwreader.get_value('filename')

    def write(self, records, **kwargs):
        with open(self.filename, 'a') as f:
            for record in records:
                f.write(record)
                f.write('\n')


class RedshiftDatastore(DataStore):
    def __init__(self, service_object_registry, *channels, **kwargs):
        DataStore.__init__(self, service_object_registry, *channels, **kwargs)


    def flush_channel_buffer_to_database(self, channel_buffer):     
        redshift_svc = self.service_object_registry.lookup('redshift')
        
        for channel_id, records in channel_buffer.items():
            print('### writing records for channel [ %s ]' % channel_id, file=sys.stderr)
            tablename = channel_id
            record_count = 0
            
            print('### kicking off multiple-insert transaction...')
            with redshift_svc.txn_scope() as session:
                try:
                    LookupRecord = eval('redshift_svc.Base.classes.%s' % tablename)
                    for record in records: 
                                                                      
                        if record.get('id') is None:
                            record['id'] = abs(hash(json.dumps(record)))                            
                                               
                        #lookup_record = LookupRecord(**record)
                        #LookupRecord = namedtuple("LookupRecord", record.keys())
                        lookup_record = LookupRecord(**record)
                        
                        print('+++ inserting record...')
                        session.add(lookup_record)
                        record_count += 1
                    session.commit()
                    print('### %d records written to channel.' % record_count, file=sys.stderr)
                except Exception as err:
                    print('!!! error writing to DB: %s' % (err), file=sys.stderr)
                    session.rollback()

        '''
        insert_stmt_tpl = 
        INSERT INTO {table} ({fieldnames})
        VALUES ({values});
        
        redshift_svc = self.service_object_registry.lookup('redshift')
        for channel_id, records in channel_buffer.items():
            tablename = channel_id
            with rs_svc.txn_scope() as session:
            for record in records:
                fields = sorted(record.keys())
                values = [record[f] for f in fields]
                insert_statement = insert_stmt_tpl.format(table=tablename,
                                                          fieldnames=','.join(fields),
                                                          values=','.join(values))
                print('### prepared insert statement:')
                print('###')                                               
                print(insert_statement)
                print('###')                           
        '''



    def write(self, records, **kwargs):
        print('### writing %s records to datastore...' % len(records), file=sys.stderr)
        channel_write_buffer = {}
        channel_id = kwargs['channel']
        if not channel_id:
            print('### This DataStore only accepts channel-mode writes. Skipping records.', file=sys.stderr)
            return

        for raw_record in records:
            record = json.loads(raw_record)
            if channel_write_buffer.get(channel_id) is None:
                channel_write_buffer[channel_id] = []
            channel_write_buffer[channel_id].append(record)
        
        self.flush_channel_buffer_to_database(channel_write_buffer)

