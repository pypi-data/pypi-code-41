import os
import json

try:
    HOME = os.path.expanduser('~')
    secret_keys = json.load(open(HOME + '/.enervee-pipeline-keys'))
except:
    secret_keys = {}

AWS_REGION = 'us-west-2'
AWS_ACCESS_KEY_ID = secret_keys.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = secret_keys.get('AWS_SECRET_ACCESS_KEY')

LOGGER_NAME = 'enervee_pipeline.sqs'
