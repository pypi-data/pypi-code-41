#!/usr/bin/python

import uuid
import os, sys
import json
from snap import common
from mercury.dataload import DataStore
from sqlalchemy.sql import text



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


    def write(self, records, **kwargs):
        print('### writing %s records to datastore...' % len(records), file=sys.stderr)
        channel_write_buffer = {}

        rs_svc = self.service_object_registry.lookup('redshift')        
        SandboxTest = rs_svc.Base.classes.test
    
        with rs_svc.txn_scope() as session:
            for raw_record in records:
                record = json.loads(raw_record)
                test_record = SandboxTest()
                for key, value in record.items():
                    setattr(test_record, key, value)
                    session.add(test_record)
                    session.commit()
                print('>>> wrote record to database: %s' % record)

        
            

