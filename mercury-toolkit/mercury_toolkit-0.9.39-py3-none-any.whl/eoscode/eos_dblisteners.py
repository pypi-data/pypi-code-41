#!/usr/bin/env python

import os, sys
import json
from snap import common
import eos_services
import pgpubsub


def psconn(svc_registry):
    secret_svc = svc_registry.lookup('secrets')
    config = secret_svc.data('jerry_rds')
    try:
        return pgpubsub.connect(**config)
    except Exception as err:
        print('!!! Error connecting to PostgreSQL event queue: %s' % err)


def handle_new_job_request(event, svc_registry): 
    print('### database insert detected...', file=sys.stderr)
    event_data = json.loads(event.payload)
    print(common.jsonpretty(event_data))

    pipeline_svc = svc_registry.lookup('pipeline')
    target_dir = pipeline_svc.log_directory
    job_tag = event_data['job_tag']

    output_file = os.path.join(os.getcwd(), target_dir, pipeline_svc.generate_job_filename(job_tag))
    print('### writing job request payload to file: %s' % output_file, file=sys.stderr)
    with open(output_file, 'w') as f:
        f.write(json.dumps(event_data))
        f.write('\n')

    
    



    