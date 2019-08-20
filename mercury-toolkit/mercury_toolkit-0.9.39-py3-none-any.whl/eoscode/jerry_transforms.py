
#!/usr/bin/env python

 
from snap import snap
from snap import common
from snap import core
import json
from snap.loggers import transform_logger as log



def sns_receive_func(input_data, service_objects, **kwargs):
    raise snap.TransformNotImplementedException('sns_receive_func')


def ping_func(input_data, service_objects, **kwargs):
    return core.TransformStatus(json.dumps({'message': 'Jerry is alive.'}))


def register_deployment_func(input_data, service_objects, **kwargs):
    pass


def register_job_func(input_data, service_objects, **kwargs):
    pass


def poll_job_status_func(input_data, service_objects, **kwargs):
    pass

def update_job_status_func(input_data, service_objects, **kwargs):
    pass

def retrieve_trained_model_func(input_data, service_objects, **kwargs):
    pass

def register_trained_model_func(input_data, service_objects, **kwargs):
    kwreader = common.KeywordArgReader('source_schema', 'target_schema', 'job_tag')
    kwreader.read(**input_data)

    job_svc = service_objects.lookup('pipeline')

    job_params = {
        'source_schema': kwreader.get_value('source_schema'),
        'target_schema': kwreader.get_value('target_schema')
    }
    tag = kwreader.get_value('job_tag')

    job_id = job_svc.request_job(tag, **job_params)

    return core.TransformStatus(json.dumps({'message': 'triggered pipeline run', 'job_id': job_id}))
