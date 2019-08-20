#!/usr/bin/env python

import os, sys
import json
import time
import sh
from snap import common
import boto3
import urllib
import uuid
import eos_services
from sqlalchemy import text
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

UNLOAD_ROLE_ARN = 'arn:aws:iam::606669716318:role/c3-shared-redshift-glue-role'


USER_PERMISSIONS_SQL_TEMPLATE = '''
GRANT USAGE ON SCHEMA {target_schema} to group c3_qdm_read;
GRANT USAGE ON SCHEMA {target_schema} to group c3_qdm_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA {target_schema} GRANT SELECT ON TABLES TO GROUP c3_qdm_read;
ALTER DEFAULT PRIVILEGES IN SCHEMA {target_schema} GRANT SELECT, INSERT, UPDATE, REFERENCES ON TABLES TO GROUP c3_qdm_admin;
GRANT CREATE ON SCHEMA {target_schema} TO GROUP c3_qdm_admin;
'''

PIPELINE_CMD = '{pipeline_script_path}/pipeline_c3.sh {database} {source_schema} {target_schema}'
PATIENT_DATA_EXPORT_CMD_TEMPLATE = "{pipeline_script_path}/scripts/xsql_c3.sh {database} '{query}'"

redshift_export_formats = {
    'csv': 'CSV',
    'parquet': 'PARQUET'
}

UNLOAD_STATEMENT_TEMPLATE = """
UNLOAD ('{query}') 
TO
'{s3_uri}'
{auth_clause}
HEADER
ALLOWOVERWRITE
DELIMITER '{delimiter}' MANIFEST VERBOSE;
"""

COHORT_SQL_TEMPLATE = '''
CREATE TABLE {tmp_schema}.{tablename} AS
(
    {cohort_query}
)
'''

DELIVERY_COHORT_TEMPLATE = '''
CREATE TABLE {tmp_schema}.delivery_cohort
AS (
WITH cohort_patient
AS
(
	select user_id from {tmp_schema}.{patient_cohort_table_name}
)
SELECT DISTINCT chai_patient_id 
FROM
c3_cdm_v5.quad_to_ptid_20190320 crosswalk,
c3_cdm_v5.patientidorgsource ptorgsrc,
c3_cdm_v5.patient_source_id ptmstr,
cohort_patient
WHERE
(crosswalk.src_patient_id = ptorgsrc.PatientID
and crosswalk.v1_org_id = ptorgsrc.orgid
and crosswalk.source_system = ptorgsrc.sourcesystem)
and ptorgsrc.PatientBestRecordID = cohort_patient.user_id
and ptmstr.clq_patient_id = crosswalk.patient_id
)
'''

generated_tables = [
    'adverse_event',
    'care_goal',
    'condition',
    'drug',
    'encounter',
    'medication',
    'patient',
    'patient_cohort',
    'patient_test',
    'radiation',
    'staging',
    'surgery',
    'tumor_exam'
]

def test_function(event_data, service_registry, **kwargs):
    print('inside trigger function.')
    print(common.jsonpretty(event_data))
    

def exec_sql(sql_cmd, service_registry):
    secret_svc = service_registry.lookup('credentials')    
    redshift_svc = eos_services.RedshiftServiceObject(**secret_svc.data('redshift'))
    connection = redshift_svc.engine.connect()
    txn = connection.begin()
    try:
        sql = text(sql_cmd)
        connection.execute(sql)
        txn.commit()
    except:
        txn.rollback()
        raise


def generate_s3_path(jobdata):
    if jobdata['dst_storage_type'] != 's3':
        raise Exception('this operation requires an input dict with dst_storage_type of "s3".')

    bucket_name = jobdata['dst_storage']['bucket_name']
    bucket_path = jobdata['dst_storage']['path']

    base_uri = 's3://%s' % bucket_name
    return os.path.join(base_uri, 'pdx_data_export', bucket_path, jobdata['job_tag'])


def run_cohort_extract(event_data, service_registry, **kwargs):
    filepath = event_data['src_path']
    job_request_data = None
    with open(filepath) as f:
        raw_request_data = f.readline()
        job_request_data = json.loads(raw_request_data)

    # the actual jobdata payload (containing the inbound queries and other data) is stored
    # in the job_request_channel database table. The inbound file event data passed to us here
    # (as loaded into the job_request_data dictionary contains a reference to the newly inserted
    # record in that database table. Specifically, it contains the relevant job_tag and the 
    # primary key of the record.

    request_pk = job_request_data['id']
    table = job_request_data['table']
    job_tag = job_request_data['job_tag']
    user_id = job_request_data['user_id']

    # retrieve the actual extract data from the RDS database
    secret_svc = service_registry.lookup('credentials')

    pg_svc = eos_services.PostgreSQLService(**secret_svc.data('jerry_rds'))
    JobRequest = pg_svc.Base.classes.job_request_channel

    jobdata = None
    try:
        with pg_svc.txn_scope() as session: 
            request_obj = session.query(JobRequest).filter(JobRequest.id == request_pk).one()
            jobdata = request_obj.request_payload

    except Exception as err:
        print('!!! error looking up job request PK %s from table %s:' % (request_pk, table), file=sys.stderr)
        print(err, file=sys.stderr)
        return

    #print(common.jsonpretty(jobdata))
    run_cohort_job(jobdata, service_registry)
    

def set_bucket_permissions(s3_uri, service_registry):
    s3_resource = boto3.resource('s3')
    s3_service = service_registry.lookup('s3')

    # pull down the manifest file
    
    '''
    policy_name = s3_svc.group_access_policy_name
    bucket_policy = s3.BucketPolicy(group_access_policy_name)
    bucket_policy.put('???')
    response = bucket_policy.put(ConfirmRemoveSelfBucketAccess=True|False,
                                         Policy='string')
    '''

def run_cohort_job(jobdata, service_registry):

    # The initial cut of patient data is performed by the COHORT QUERY.
    # The data extract is done by the PATIENT QUERY, which filters on the patient IDs
    # returned from the COHORT QUERY
    job_tag = jobdata['job_tag']
    raw_cohort_query = jobdata['cohort_query']
    cohort_query = urllib.parse.unquote(raw_cohort_query)
    raw_patient_data_query = jobdata['patient_data_query']
    patient_query_template = urllib.parse.unquote(raw_patient_data_query)
    
    tmp_schema = jobdata['temp_schema_name']
    exec_sql('CREATE SCHEMA %s' % tmp_schema, service_registry)

    patient_cohort_table_name = 'patient_cohort'
    create_table_statement = COHORT_SQL_TEMPLATE.format(tmp_schema=tmp_schema,
                                                        tablename=patient_cohort_table_name,
                                                        cohort_query=cohort_query)
    print('### running initial query:')
    print(create_table_statement)    
    exec_sql(create_table_statement, service_registry)
    print('### initial query completed.')
    
    print('### patient query template:')
    print(patient_query_template)
    
    print('### populating patient query template with temp schema %s...' % tmp_schema)
    patient_query_block = patient_query_template.format(
        cohort_sql=cohort_query,
        src_schema=jobdata['src_storage']['schema_name'],
        dst_schema=tmp_schema,
        patient_cohort_table=patient_cohort_table_name
    )
    print('### patient query template populated.')
    print('### PATIENT QUERY:')
    print(patient_query_block)
    jerry_svc = service_registry.lookup('job_mgr_api')    
    try:
        s3_svc = service_registry.lookup('s3')
        bucket_uri = None
        if jobdata['dst_storage_type'] == 's3':
            s3_queries = []
            # generate UNLOAD commands against extract tables
            
            bucket_uri = generate_s3_path(jobdata)
            for table_name in generated_tables:
                table_query='SELECT * FROM %s.%s' % (tmp_schema, table_name)
                export_sql_string = UNLOAD_STATEMENT_TEMPLATE.format(query=table_query,
                                                                     s3_uri=os.path.join(bucket_uri, table_name),
                                                                     auth_clause="iam_role '%s'" % s3_svc.unload_arn,
                                                                     delimiter='|')
                s3_queries.append(export_sql_string)
            target_query = patient_query_block + '\n' + '\n'.join(s3_queries)

        else:
            target_query = patient_query_block

        print('### running export query:') 
        print(target_query)        
        exec_sql(target_query, service_registry)
        print('### export query completed.')

        if jobdata['dst_storage_type'] == 's3':
            # delete generated temp tables
            exec_sql('DROP SCHEMA %s CASCADE' % tmp_schema, service_registry)

            # set_bucket permissions
            set_bucket_permissions(bucket_uri, service_registry)
        else:
            # if destination is database, issue GRANT query
            grant_sql = USER_PERMISSIONS_SQL_TEMPLATE.format(target_schema=tmp_schema)
            exec_sql(grant_sql, service_registry)

            

            
        print('### cohort extract job %s completed successfully.' % job_tag)
        jerry_svc.notify_job_completed(jobdata['job_tag'])

    except Exception as err:
        # report job failure to Jerry endpoint
        print('!!! cohort extract job %s FAILED.' % job_tag)
        print('!!! Exception of type %s thrown:' % err.__class__.__name__)
        print(err)
        jerry_svc.notify_job_failed(job_tag)


def run_pipeline(event_data, service_registry, **kwargs):
    # if we want to bulletproof this function against incomplete event data...
    validator = common.KeywordArgReader('src_path', 'dest_path', 'event_type', 'is_directory', 'time_received')
    validator.read(**event_data)
    
    print('### inside registered handler function.')

    filepath = event_data['src_path']
    print("### stub handler for file %s" % filepath)
    if not filepath.find('pipeline'):
        return None
    
    jobdata = None
    with open(filepath) as f:
        raw_jobdata = f.readline()
        jobdata = json.loads(raw_jobdata)

    print(common.jsonpretty(jobdata))
    
    pipeline_command_string = PIPELINE_CMD.format(pipeline_dir=os.getcwd())
    print(pipeline_command_string)
    
    source_schema = jobdata['source_schema']
    target_schema = jobdata['target_schema']
    pcmd = sh.Command(pipeline_command_string)
    for line in pcmd('assets_qdm.txt', source_schema, target_schema, _err=sys.stdout, _iter=True):
        print(line)


def build_model(event_data, service_registry, **kwargs):
    print('### Someone requested a model-build with the following payload:')
    print(event_data)
    jerry = service_registry.lookup('job_mgr_api')
    #jerry.notify_job_completed(job_tag)


