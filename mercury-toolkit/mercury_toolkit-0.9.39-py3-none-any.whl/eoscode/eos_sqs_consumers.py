#!/usr/bin/env python

import os, sys
import json
from snap import common
from eos_services import S3Key
from eos_watch_triggers import run_cohort_job


def test_handler(message, receipt_handle, service_tbl):

    service_registry = common.ServiceObjectRegistry(service_tbl)
    s3_svc = service_registry.lookup('s3')
    print('### Inside SQL message handler function.')
    print("### message follows:")

    # unpack SQS message to get SNS notification about S3 file upload
    message_body_raw = message['Body']
    message_body = json.loads(message_body_raw)
    event_data = json.loads(message_body['Message'])

    print(common.jsonpretty(event_data))

    # for each file that has been uploaded to S3, download and use the information
    # to kick off a cohort extract job.
    #
    # AWS documentation suggests that there will only ever be a single record, so 
    # address the structure as such
    record = event_data['Records'][0]
    # ignore non-S3 events
    if record['eventSource'] != 'aws:s3':
        return
    bucket_name = record['s3']['bucket']['name']
    object_key = record['s3']['object']['key']
    object_size = record['s3']['object']['size']
    # TODO: set a limit on file size?

    s3key = S3Key(bucket_name, object_key)
    print('### received news of S3 object upload: %s' % s3key.uri)

    jsondata = None
    try:
        jsondata = s3_svc.download_json(bucket_name, object_key)
        print('### JSON payload data:')
        print(common.jsonpretty(jsondata))
    except Exception as err:
        print('Error retrieving or converting JSON object data from URI %s.' % s3key.uri)
        print(err)
        return

    jerry_svc = service_registry.lookup('job_mgr_api')
    job_tag = jsondata['job_tag']
    
    try:
        print('>>> starting cohort extract job with tag: [ %s ]' % job_tag)
        run_cohort_job(jsondata, service_registry)
    except Exception as err:
        jerry_svc.notify_job_failed(job_tag)
        print('!!! Notified job mgr of FAILURE for job tag %s' % job_tag)
        print('!!! Exception of type %s thrown:' % err.__class__.__name__)
        print(err)