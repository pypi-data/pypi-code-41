#!/usr/bin/env python

from profiling import Profiler


class FillRateProfiler(Profiler):
    def __init__(self, table_name, *columns, **kwargs):
        Profiler.__init__(self, table_name, *columns, **kwargs)


    def _profile(self, record_generator, service_registry, **kwargs):
        limit = kwargs.get('limit', -1)        
        profile_dict = {}
        for colname in self.columns:
            profile_dict[colname] = 0

        rec_count = 0
        for input_record in record_generator:
            for colname in self.columns:
                value = input_record.get(colname)
                if value is None or value in self.null_value_equivalents[colname]:
                    profile_dict[colname] += 1

            rec_count += 1
            if rec_count == limit:
                break

            if not rec_count % 100000:
                print('%s records processed.' % rec_count)
        return profile_dict, rec_count