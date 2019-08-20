#!/usr/bin/env python

from sqlalchemy import text
from collections import namedtuple


DataError = namedtuple('DataError', 'type message')
DataFlag = namedtuple('DataFlag', 'type message')

chai_test = '''
SELECT
    chai_patient_id ,
    'ER' molecular_marker,
    labtestvalue_codelabel diagnostic_value
FROM {data_drop_schema}.laboratorytestperformed
WHERE labtestname_codelabel LIKE 'Estrog%'
AND labtestvalue_codelabel IS NOT NULL
AND labtestvalue_codelabel NOT LIKE 'Unknown'
'''


bodytemp_query = '''
SELECT chai_patient_id, examname_codelabel, examvaluenumeric, examunit_codelabel
    FROM {data_drop_schema}.physicalexamperformed
    WHERE examname_codelabel = 'Body Temperature'
    AND (examunit_codelabel IS NULL OR examunit_codelabel = '')    
'''


def generate_records(sql_query, service_registry, **kwargs):
    redshift_svc = service_registry.lookup('redshift')    
    sql = text(sql_query)
    result = redshift_svc.engine.execute(sql)
    for record in result:
        yield record


def build_body_temp_outputs(record_generator):
    outputs = {}
    outputs['record_count'] = 0
    outputs['distinct_patient_count'] = 0
    outputs['min_temp_value']  = float(0)
    outputs['max_temp_value'] = float(0)
    outputs['num_null_temp_values'] = 0
    outputs['num_temp_values_over_116'] = 0
    print('### Inside output builder function.')
    unique_patient_ids = set()
    first_record = True
    for record in record_generator:

        if any([
            record['examvaluenumeric'] is None,
            record['examvaluenumeric'] == ''
        ]):
            outputs['num_null_temp_values'] += 1
        else:
            outputs['min_temp_value'] = float(record['examvaluenumeric'])
        
            first_record = False
            recorded_temperature = float(record['examvaluenumeric'])
            if recorded_temperature > outputs['max_temp_value']:
                outputs['max_temp_value'] = recorded_temperature

            if not first_record and recorded_temperature < outputs['min_temp_value']:
                outputs['min_temp_value'] = recorded_temperature

            if recorded_temperature > float(116):
                outputs['num_temp_values_over_116'] += 1

        outputs['record_count'] += 1
        unique_patient_ids.add(record['chai_patient_id'])
        if not outputs['record_count'] % 1000:
            print('### %d records processed.' % outputs['record_count'])

    print('### %d records processed.' % outputs['record_count'])

    record_count = outputs['record_count']
    outputs['percent_null_temp_values'] = (outputs['num_null_temp_values'] / record_count) * 100
    outputs['percent_temp_values_over_116'] = (outputs['num_temp_values_over_116'] / record_count) * 100    
    outputs['distinct_patient_count'] = len(unique_patient_ids)
    return outputs


def analyze_body_temp_outputs(job_output_dict):
    '''
    {"job_output": {"num_null_temp_values": 97079, 
    "distinct_patient_count": 207051, 
    "max_temp_value": 973498.2, 
    "min_temp_value": 37.1, 
    "record_count": 3017011}, 
    "analysis_ouptut": []}
    '''

    analysis_output = {
        'flags': [],
        'errors': []
    }

    if job_output_dict['percent_null_temp_values'] > 5:
        analysis_output['flags'].append('excessive_null_temperature_values')

    if job_output_dict['num_temp_values_over_116'] > 0:
        analysis_output['errors'].append('excessive_high_temperature')
    
    analysis_output['flag_'] = False
    if job_output_dict['distinct_patient_count'] < 200000:
        analysis_output['flags'].append('low_patient_count')

    return analysis_output    


def build_chai_test_outputs(record_generator):
    outputs = {}
    outputs['diagnostic_value_null_or_empty'] = 0
    outputs['num_diagnostic_values_unrecognized'] = 0
    count = 0
    for record in record_generator:
        count += 1
        if record['diagnostic_value'] == None or record['diagnostic_value'] == '':
            outputs['diagnostic_value_null_or_empty'] += 1
            outputs['num_diagnostic_values_unrecognized'] += 1

    outputs['record_count'] = count
    return outputs


def count_colums_test(record_generator):
    outputs = {}
    for record in record_generator:
        outputs['column_count'] = len(record.keys())
    return outputs


def chai_test_analyzer(job_output_dict):
    conditions = []
    rec_count = job_output_dict['record_count']
    missing_diag_value = job_output_dict['diagnostic_value_null_or_empty']

    if missing_diag_value > rec_count / 2:
        msg = 'More than 50% of the ER results null or empty.'
        conditions.append(DataFlag(type='flag', message=msg))

    return conditions

