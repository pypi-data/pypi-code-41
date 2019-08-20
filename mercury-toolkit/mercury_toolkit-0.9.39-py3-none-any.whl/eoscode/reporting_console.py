#!/usr/bin/env python

'''
Usage:
    reporting_console --config <configfile> --report <report_name>
'''


import os
import sys
from datetime import date, datetime
from snap import snap, common
import docopt
import reporting as rpt


COUNT_QUERY = '''
SELECT count(Distinct PatientBestRecordID) AS patient_count FROM `{project}.{dataset}.patients`
'''

DIAGNOSTIC_GROUP_QUERY = '''
SELECT DISTINCT PatientBestRecordID from `{project}.{dataset}.DiagnosisActive`
WHERE
{filter_clause}
AND
DiagnosisDate > '{cutoff_date}'
'''

TEMP_TABLE_QUERY = '''
CREATE TABLE `{project}.{dataset}.{temp_table_name}`
AS
SELECT DISTINCT PatientBestRecordID 
FROM 
`{project}.{dataset}.DiagnosisActive`
WHERE
{filter_clause}
'''

def main(args):
    configfile = args['<configfile>']
    yaml_config = common.read_config_file(configfile)

    report_engine = rpt.BigQueryReportingEngine()

    count_query_input_fields = [
        rpt.ReportInputField(name='project', input_class=str),
        rpt.ReportInputField(name='dataset', input_class=str)     
    ]

    dg_query_input_fields = [
        rpt.ReportInputField(name='project', input_class=str),
        rpt.ReportInputField(name='dataset', input_class=str),
        rpt.ReportInputField(name='filter_clause', input_class=str)
    ]

    tt_query_input_fields = [
        rpt.ReportInputField(name='temp_table_name', input_class=str),
        rpt.ReportInputField(name='project', input_class=str),
        rpt.ReportInputField(name='dataset', input_class=str),
        rpt.ReportInputField(name='filter_clause', input_class=str)  
    ]

    qs1 = rpt.ReportQuerySpec(COUNT_QUERY, *count_query_input_fields)
    qs2 = rpt.ReportQuerySpec(DIAGNOSTIC_GROUP_QUERY, *dg_query_input_fields)
    qs3 = rpt.ReportQuerySpec(TEMP_TABLE_QUERY, *tt_query_input_fields)
    
    report_engine.add_report(qs1, 'patient_count')
    report_engine.add_report(qs2, 'diagnostics')
    report_engine.add_report(qs3, 'create_temp_table')

    predicates = [
        rpt.FilterPredicateLike('DiagnosisCode_Code', '185%'),
        rpt.FilterPredicateLike('DiagnosisCode_Code', '233.4%'),
        rpt.FilterPredicateLike('DiagnosisCode_Code', 'C61%'),
        rpt.FilterPredicateLike('DiagnosisCode_Code', 'D07.5%')
    ]

    '''
    resultset = report_engine.run('diagnostics',
                                  project='phi-hello-world',
                                  dataset='creed_d25_201810_sup',
                                  filter_clause=rpt.Or(*predicates).sql(),
                                  cutoff_date=datetime.strptime('12-31-2007', '%m-%d-%Y').date(),
                                  debug=True)
    '''
    
    resultset = report_engine.run('create_temp_table',
                                  project='phi-hello-world',
                                  dataset='creed_d25_201810_sup',
                                  temp_table_name='pdx_temp_tbl',
                                  filter_clause=rpt.Or(*predicates).sql(),
                                  debug=True)

    '''
    resultset = report_engine.run('patient_count',
                                  project='phi-hello-world',
                                  dataset='creed_d25_201811_sup')
    '''

    print(common.jsonpretty(resultset))


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    main(args)