#!/usr/bin/env python

import os, sys
import uuid
import time
import json
import copy
from contextlib import contextmanager
from collections import namedtuple

import requests
import boto3
import sqlalchemy as sqla
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy_utils import UUIDType

from snap import common


Base = declarative_base()

'''
TODO: try integrating the Redshift settings:
keepalives=1
keepalives_interval=60
keepalives_idle="60"
'''

class AWSSecretService(object):
    def __init__(self, **kwargs):
        deploy_types = ['local', 'aws']
        required_fields = [
            'deploy_type',
            'client_secret_name',
            'object_tags',    
            'outputs',
            'region'
        ]
        kwreader = common.KeywordArgReader(*required_fields)
        kwreader.read(**kwargs)
        self.deploy_type = kwreader.get_value('deploy_type')
        if self.deploy_type not in deploy_types:
            raise Exception('allowed deploy_type values are: %s' % deploy_types)
        
        self.secrets = {}
        self.defaults = kwreader.get_value('outputs')
        self.object_tag_map = kwreader.get_value('object_tags')

        if set(self.object_tag_map.keys()) != set(self.defaults.keys()):
            raise Exception("The outputs section must have a matching key for each object tag.")

        if self.deploy_type == 'aws':
            self.asm_client = boto3.client('secretsmanager', region_name=kwreader.get_value('region'))
            self.secret_name = kwreader.get_value('client_secret_name')
            self.secrets = self.asm_client.get_secret_value(SecretId=self.secret_name)
                        
        if self.deploy_type == 'local':
            for section_name, section_config in self.defaults.items():            
                for key, value in section_config.items():
                    section_config[key] = common.load_config_var(value)


    def data(self, object_tag):
        if object_tag not in self.defaults.keys():
            raise Exception('No configuration tag "%s" specified. Please check your YAML file.' % object_tag)
        
        if self.deploy_type == 'local':
            return self.defaults[object_tag]

        # deploy_type is 'aws', so pull data from SecretsManager        
        return self.update_config(object_tag, **copy.deepcopy(self.defaults[object_tag]))


    def get_object(self, tag):
        obj_dict = json.loads(self.secrets['SecretString'])
        attr_name = self.object_tag_map.get(tag)
        if not attr_name:
            raise Exception('No value for object_tag "%s" present in the source config. Please check your YAML file.' % tag)
        
        secrets_obj = obj_dict.get(attr_name)
        if not secrets_obj:
            raise Exception('No attribute "%s" present in SecretString block from secret ID %s.' 
                            % (attr_name, self.secret_name))
        return secrets_obj


    def update_config(self, tag, **kwargs):    
        secrets_obj = self.get_object(tag)

        kwargs['database'] = secrets_obj['database']['dbname']
        kwargs['host'] = secrets_obj['database']['host']        
        kwargs['username'] = secrets_obj['database']['user']
        kwargs['password'] = secrets_obj['database']['password']        
        return kwargs   


class PipelineJobService(object):
    def __init__(self, **kwargs):
        print('### initializing pipeline job service...', file=sys.stderr)
        kwreader = common.KeywordArgReader('log_directory')
        kwreader.read(**kwargs)
        self.log_directory = kwreader.get_value('log_directory')
        print('### designated log directory is [ %s ].' % self.log_directory, file=sys.stderr)

    
    def generate_job_filename(self, tag):
        id = uuid.uuid4()
        return 'pipeline.%s.%s.json' % (tag, id)

    '''
    def request_job_start(self, job_tag, **kwargs):
        job_id = self.generate_job_id(job_tag)
        jobfile = os.path.join(self.log_directory, job_id + '.json')
        with open(jobfile, 'a') as f:
            f.write(json.dumps(kwargs))
            f.write('\n')
        return job_id
    '''

APIEndpoint = namedtuple('APIEndpoint', 'host port path method')

class APIError(Exception):
    def __init__(self, url, method, status_code, **kwargs):
        super.__init__(self, 
                       'Error sending %s request to URL %s with payload %s: status code %s' % 
                       method, url, kwargs, status_code)


class S3Key(object):
    def __init__(self, bucket_name, s3_object_path):
        self.bucket = bucket_name
        self.folder_path = self.extract_folder_path(s3_object_path)
        self.object_name = self.extract_object_name(s3_object_path)
        self.full_name = s3_object_path

    def extract_folder_path(self, s3_key_string):
        if s3_key_string.find('/') == -1:
            return ''
        key_tokens = s3_key_string.split('/')
        return '/'.join(key_tokens[0:-1])

    def extract_object_name(self, s3_key_string):
        if s3_key_string.find('/') == -1:
            return s3_key_string
        return s3_key_string.split('/')[-1]

    def __str__(self):
        return self.full_name

    @property
    def uri(self):
	    return os.path.join('s3://', self.bucket, self.full_name)



s3_auth_error_mesage = '''
S3ServiceObject must pe passed the "aws_key_id" and "aws_secret_key"
parameters if the "auth_via_iam" init param is not set (or is False).'''


class S3Service(object):
    def __init__(self, **kwargs):
        kwreader = common.KeywordArgReader('local_temp_path', 'region')
        kwreader.read(**kwargs)

        self.local_tmp_path = kwreader.get_value('local_temp_path')
        self.region = kwreader.get_value('region')
        self.s3session = None
        self.aws_access_key_id = None
        self.aws_secret_access_key = None
        self.unload_arn = kwreader.get_value('unload_arn')

        # we set this to True if we are initializing this object from inside an AWS Lambda,
        # because in that case we do not require the aws credential parameters to be set.
        # The default is False, which is what we want when we are creating this object
        # in a normal (non-AWS-Lambda) execution context: clients must pass in credentials.
        should_authenticate_via_iam = kwargs.get('auth_via_iam', False)

        if not should_authenticate_via_iam:
            log.info("NOT authenticating via IAM. Setting credentials now.")
            self.aws_access_key_id = kwargs.get('aws_key_id')
            self.aws_secret_access_key = kwargs.get('aws_secret_key')
            if not self.aws_secret_access_key or not self.aws_access_key_id:
                raise Exception(s3_auth_error_mesage)           
            self.s3client = boto3.client('s3',
                                         aws_access_key_id=self.aws_access_key_id,
                                         aws_secret_access_key=self.aws_secret_access_key)
        else:
            self.s3client = boto3.client('s3', region_name=self.region)
 

    def upload_object(self, local_filename, bucket_name, bucket_path=None):
        s3_path = None
        with open(local_filename, 'rb') as data:
            base_filename = os.path.basename(local_filename)
            if bucket_path:
                s3_path = os.path.join(bucket_path, base_filename)
            else:
                s3_path = base_filename

            self.s3client.upload_fileobj(data, bucket_name, s3_path)

        return S3Key(bucket_name, s3_path)

    
    def upload_bytes(self, bytes_obj, bucket_name, bucket_path):
        s3_key = bucket_path
        self.s3client.put_object(Body=bytes_obj, Bucket=bucket_name, Key=s3_key)
        return s3_key
    
    '''
    def download_object(self, bucket_name, s3_key_string):
        #s3_object_key = S3Key(s3_key_string)
        local_filename = os.path.join(self.local_tmp_path, s3_object_key.object_name)
        with open(local_filename, "wb") as f:
            self.s3client.download_fileobj(bucket_name, s3_object_key.full_name, f)

        return local_filename
    '''

    def download_json(self, bucket_name, s3_key_string):
        #s3_object_key = S3Key(s3_key_string)

        obj = self.s3client.get_object(Bucket=bucket_name, Key=s3_key_string)
        return json.loads(obj['Body'].read().decode('utf-8'))


class JerryAPIService(object):
    def __init__(self, **kwargs):
        kwreader = common.KeywordArgReader('host', 'port')
        kwreader.read(**kwargs)
        self.hostname = kwreader.get_value('host')
        self.port = int(kwreader.get_value('port'))        
        self.poll_job = APIEndpoint(host=self.hostname, port=self.port, path='job', method='GET')
        self.update_job_status = APIEndpoint(host=self.hostname, port=self.port, path='jobstatus', method='POST')

    def endpoint_url(self, api_endpoint):
        url = 'http://{host}:{port}'.format(host=api_endpoint.host, port=api_endpoint.port)
        return os.path.join(url, api_endpoint.path)

    def _call_endpoint(self, endpoint, payload, **kwargs):        
        url_path = self.endpoint_url(endpoint)
        if endpoint.method == 'GET':                        
            print('calling endpoint %s using GET...' % url_path)
            return requests.get(url_path, params=payload)
        if endpoint.method == 'POST':
            print('calling endpoint %s using POST...' % url_path)
            return requests.post(url_path, data=payload)

    def notify_job_completed(self, job_tag, **kwargs):
        payload = {'job_tag': job_tag, 'status': 'completed'}
        response = self._call_endpoint(self.update_job_status,
                                       payload)
        if response.status_code != 200:
            raise APIError(self.endpoint_url(self.update_job_status),
                           self.update_job_status.method,
                           response.status_code)


    def notify_job_failed(self, job_tag, **kwargs):
        response = self._call_endpoint(self.update_job_status,
                                       {'job_tag': job_tag,
                                        'status': 'failed'})
        if response.status_code != 200:
            raise APIError(self.endpoint_url(self.update_job_status),
                           self.update_job_status.method,
                           response.status_code)


class JobDispatcher(object):
    def __init__(self, job_manager, event_handler_module_name, **kwargs):        
        self.job_manager = job_manager
        self.handler_module = event_handler_module_name
        self.dispatch_table = {}

    def register_job_event_handler(self,
                                   job_identifier,
                                   event_tag,
                                   handler_func_name):
        handler_func = None # TODO: resolve module and function name to function
        self.dispatch_table[(job_identifier, event_tag)] = handler_func
        
    def start_job(self, job_identifier, **kwargs):
        if self.job_manager.start_job(job_identifier):
            return True
        return False

    def poll_job_status_match(self, job_identifier, status_tag):
        '''return True if job matches the given status, else False
        '''
        if self.job_manager.job_status(job_identifier) == status_tag:
            return True
        return False


class PipelineJobManager(object):
    def __init__(self, **kwargs):
        pass


class PostgresPipelineJobManager(PipelineJobManager):
    def __init__(self, **kwargs):
        super.__init__(self, **kwargs)


    def _start_job(self, job_identifier):
        # insert record into managed jobs table
        pass

    def job_status(self, job_identifier):
        # TODO: issue db query
        pass


class RedshiftServiceObject(object):
    def __init__(self, **kwargs):    
        self.host = kwargs['host']
        self.db_name = kwargs['database']
        self.port = kwargs['port']
        self.username = kwargs['username']
        self.schema = kwargs['schema']
        password = kwargs['password']
        
        self.metadata = None
        self.engine = None
        self.session_factory = None
        self.Base = None
                
        url_template = '{db_type}://{user}:{passwd}@{host}:{port}/{database}'
        db_url = url_template.format(db_type='redshift+psycopg2',
                                     user=self.username,
                                     passwd=password,
                                     host=self.host,
                                     port=self.port,
                                     database=self.db_name)
        retries = 0
        connected = False
        while not connected and retries < 3:
            try:
                print('### Connecting to Redshift DB...', file=sys.stderr)                
                self.engine = sqla.create_engine(db_url)
                
                print('created engine, performing reflection...')
                self.metadata = MetaData(schema=self.schema)
                #self.metadata = MetaData()
                self.metadata.reflect(bind=self.engine)
                #self.metadata.reflect(self.engine)
                self.Base = automap_base(bind=self.engine, metadata=self.metadata)
                #self.Base = automap_base(bind=self.engine)
                #
                print('automapped data types, preparing base...')
                self.Base.prepare(self.engine, reflect=True)
                #self.Base.prepare()                
                self.session_factory = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
                print('created session factory')
                connected = True
                print('### Connected to Redshift DB.', file=sys.stderr)
                
            except Exception as err:
                print(err)
                print(err.__class__.__name__)
                print(err.__dict__)
                time.sleep(1)
                retries += 1
            
        if not connected:
            raise Exception('!!! Unable to connect to Redshift db on host %s at port %s.' % (self.host, self.port))
        

    @contextmanager
    def txn_scope(self):
        session = self.session_factory()        
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


    @contextmanager    
    def connect(self):
        connection = self.engine.connect()
        try:
            yield connection
        finally:
            connection.close()


class PostgreSQLService(object):
    def __init__(self, **kwargs):
        
        self.db_name = kwargs['database']
        self.host = kwargs['host']
        self.port = int(kwargs.get('port', 5432))
        self.username = kwargs['username']
        self.password = kwargs['password']        
        self.schema = kwargs['schema']
        self.metadata = None
        self.engine = None
        self.session_factory = None
        self.Base = None
                
        url_template = '{db_type}://{user}:{passwd}@{host}/{database}'
        db_url = url_template.format(db_type='postgresql+psycopg2',
                                     user=self.username,
                                     passwd=self.password,
                                     host=self.host,
                                     port=self.port,
                                     database=self.db_name)
        
        retries = 0
        connected = False
        while not connected and retries < 3:
            try:
                self.engine = sqla.create_engine(db_url, echo=False)
                self.metadata = MetaData(schema=self.schema)
                self.Base = automap_base(bind=self.engine, metadata=self.metadata)
                self.Base.prepare(self.engine, reflect=True)
                self.metadata.reflect(bind=self.engine)
                self.session_factory = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
                connected = True
                print('### Connected to PostgreSQL DB.', file=sys.stderr)
                
            except Exception as err:
                print(err)
                print(err.__class__.__name__)
                print(err.__dict__)
                time.sleep(1)
                retries += 1
            
        if not connected:
            raise Exception('!!! Unable to connect to PostgreSQL db on host %s at port %s.' % (self.host, self.port))

    @contextmanager
    def txn_scope(self):
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


    @contextmanager    
    def connect(self):
        connection = self.engine.connect()
        try:
            yield connection
        finally:
            connection.close()
