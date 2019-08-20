
#!/usr/bin/env python

#
# Generated Flask routing module for SNAP microservice framework
#



from flask import Flask, request, Response
from snap import snap
from snap import core
import logging
import json
import argparse
import sys
from snap.loggers import request_logger as log

sys.path.append('/home/dtaylor/workshop/precision/pdx_eos')
import eos_transforms

f_runtime = Flask(__name__)

if __name__ == '__main__':
    print('starting SNAP microservice in standalone (debug) mode...')
    f_runtime.config['startup_mode'] = 'standalone'
    
else:
    print('starting SNAP microservice in wsgi mode...')
    f_runtime.config['startup_mode'] = 'server'

app = snap.setup(f_runtime)
xformer = core.Transformer(app.config.get('services'))


#-- snap exception handlers ---

xformer.register_error_code(snap.NullTransformInputDataException, snap.HTTP_BAD_REQUEST)
xformer.register_error_code(snap.MissingInputFieldException, snap.HTTP_BAD_REQUEST)
xformer.register_error_code(snap.TransformNotImplementedException, snap.HTTP_NOT_IMPLEMENTED)

#------------------------------



#-- snap data shapes ----------


default = core.InputShape("default")

trigger = core.InputShape("trigger")
trigger.add_field('source_schema', True)
trigger.add_field('target_schema', True)
trigger.add_field('job_tag', True)

default = core.InputShape("default")


#------------------------------


#-- snap transform loading ----
xformer.register_transform('sns_receive', default, eos_transforms.sns_receive_func, 'application/json')
xformer.register_transform('pipeline_job', trigger, eos_transforms.pipeline_job_func, 'application/json')
xformer.register_transform('ping', default, eos_transforms.ping_func, 'application/json')

#------------------------------



@app.route('/sns', methods=['POST'])
def sns_receive():
    try:
        if app.debug:
            # dump request headers for easier debugging
            log.info('### HTTP request headers:')
            log.info(request.headers)

        input_data = {}
        request.get_data()
        input_data.update(core.map_content(request))
        
        transform_status = xformer.transform('sns_receive', input_data, headers=request.headers)        
        output_mimetype = xformer.target_mimetype_for_transform('sns_receive')

        if transform_status.ok:
            return Response(transform_status.output_data, status=snap.HTTP_OK, mimetype=output_mimetype)
        return Response(json.dumps(transform_status.user_data), 
                        status=transform_status.get_error_code() or snap.HTTP_DEFAULT_ERRORCODE, 
                        mimetype=output_mimetype) 
    except Exception as err:
        log.error("Exception thrown: ", exc_info=1)        
        raise err


@app.route('/trigger-pipeline', methods=['GET'])
def pipeline_job():
    try:
        if app.debug:
            # dump request headers for easier debugging
            log.info('### HTTP request headers:')
            log.info(request.headers)

        input_data = {}                
        input_data.update(request.args)
        
        transform_status = xformer.transform('pipeline_job',
                                             core.convert_multidict(input_data),
                                             headers=request.headers)        
        output_mimetype = xformer.target_mimetype_for_transform('pipeline_job')

        if transform_status.ok:
            return Response(transform_status.output_data, status=snap.HTTP_OK, mimetype=output_mimetype)
        return Response(json.dumps(transform_status.user_data), 
                        status=transform_status.get_error_code() or snap.HTTP_DEFAULT_ERRORCODE, 
                        mimetype=output_mimetype) 
    except Exception as err:
        log.error("Exception thrown: ", exc_info=1)        
        raise err


@app.route('/ping', methods=['GET'])
def ping():
    try:
        if app.debug:
            # dump request headers for easier debugging
            log.info('### HTTP request headers:')
            log.info(request.headers)

        input_data = {}                
        input_data.update(request.args)
        
        transform_status = xformer.transform('ping',
                                             core.convert_multidict(input_data),
                                             headers=request.headers)        
        output_mimetype = xformer.target_mimetype_for_transform('ping')

        if transform_status.ok:
            return Response(transform_status.output_data, status=snap.HTTP_OK, mimetype=output_mimetype)
        return Response(json.dumps(transform_status.user_data), 
                        status=transform_status.get_error_code() or snap.HTTP_DEFAULT_ERRORCODE, 
                        mimetype=output_mimetype) 
    except Exception as err:
        log.error("Exception thrown: ", exc_info=1)        
        raise err





if __name__ == '__main__':
    #
    # If we are loading from command line,
    # run the Flask app explicitly
    #
    app.run(host='0.0.0.0', port=5000)

