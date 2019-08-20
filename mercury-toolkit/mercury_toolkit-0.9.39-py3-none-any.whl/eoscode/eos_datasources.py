#!/usr/bin/env python

import datetime
from snap import common


class EOSLookupDatasource(object):
    def __init__(self, service_object_registry):
        self.services = service_object_registry

    def lookup_labtestdate(self, target_field_name, source_record, field_value_map):
       
        if not source_record.get('labtestdate'):
            return None
        source_date = source_record['labtestdate']
        return source_date.split('T')[0]
        

    def lookup_death_indicator(self, target_field_name, source_record, field_value_map):
        #redshift_svc = self.services.lookup('redshift')        
        return 5

    def default_tf(self, source_record):
        target_record = {}
        for key, value in source_record.items():
            if key == 'Source':
                target_record['src'] = value
                continue
            if key == 'Method':
                target_record['mtd'] = value
                continue
            target_record[key.lower()] = value
            
        return target_record
        
    def lookup_is_us_state(self, target_field_name, source_record, field_value_map):        
        if source_record.get('USStates', '') == 'Y':
            return True
        return False
