#!/usr/bin/env python


import os
import uuid
from snap import snap
from snap import common
from mercury import sqldbx as sqlx

from contextlib import contextmanager
import sqlalchemy as sqla
from sqlalchemy.ext.automap import automap_base
from mercury_services.aws_services import S3ServiceObject

from sqlalchemy import MetaData, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy_utils import UUIDType


Base = declarative_base()


class PostgreSQLServiceObject(object):
    def __init__(self, **kwargs):
        self.db = sqlx.PostgreSQLDatabase(kwargs['host'],
                                          kwargs['database'])
        self.username = kwargs['username']
        self.password = kwargs['password']        
        self.schema = kwargs['schema']
        self.data_manager = None
        self.db.login(self.username, self.password)        
        self.data_manager = sqlx.PersistenceManager(self.db)
        self.Base = automap_base()
        self.Base.prepare(self.db.engine, reflect=True)


    @property
    def data_manager(self):
        return self.data_manager


    @property
    def database(self):
        return self.db


    def get_connection(self):
        return self.db.engine.connect()


    @contextmanager
    def txn_scope(self):
        session = self.db.get_session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


class MSSQLServiceObject(object):
    def __init__(self, logger, **kwargs):
        kwreader = common.KeywordArgReader('host', 'username', 'database', 'password')
        kwreader.read(**kwargs)

        self.log = logger
        self.host = kwreader.get_value('host')
        self.port = int(kwreader.get_value('port') or 1433)
        self.username = kwreader.get_value('username')
        self.db_name = kwreader.get_value('database')
        self.password = kwreader.get_value('password')
        self.db = sqlx.SQLServerDatabase(self.host, self.db_name, self.port)
        self.db.login(self.username, self.password)
        self._data_manager = sqlx.PersistenceManager(self.db)


    @property
    def data_manager(self):
        return self._data_manager

    @property
    def database(self):
        return self.db


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
                self.engine = sqla.create_engine(db_url, echo=False)
                self.metadata = MetaData(schema=self.schema)
                self.Base = automap_base(bind=self.engine, metadata=self.metadata)
                self.Base.prepare(self.engine, reflect=True)
                self.metadata.reflect(bind=self.engine)
                self.session_factory = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
                connected = True
                print('### Connected to Redshift DB.')
                
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

        
    def get_connection(self):
        return self.engine.connect()


class CouchbaseServiceObject():
    def __init__(self, **kwargs):
        self.host = kwargs['host']
        self.data_bucket_name = kwargs['data_bucket_name']
        self.journal_bucket_name = kwargs['journal_bucket_name']
        self.cache_bucket_name = kwargs['cache_bucket_name']

        self.couchbase_server = cbx.CouchbaseServer(self.host)
        self.data_manager = cbx.CouchbasePersistenceManager(self.couchbase_server, self.data_bucket_name)
        self.journal_manager = cbx.CouchbasePersistenceManager(self.couchbase_server, self.journal_bucket_name)
        self.cache_manager = cbx.CouchbasePersistenceManager(self.couchbase_server, self.cache_bucket_name)


    def insert_record(self, record_type_name, record_dict):
        cb_record = cbx.CouchbaseRecordBuilder(record_type_name).add_fields(record_dict).build()
        return self.data_manager.insert_record(cb_record)


class RedisServiceObject():
    def __init__(self, **kwargs):        
        self.host = kwargs['host']
        self.port = kwargs.get('port', 6379)
        self.redis_server = redisx.RedisServer(self.host, self.port)
        self.transformed_record_queue_name = kwargs['transformed_record_queue_name']
        self.raw_record_queue_name = kwargs['raw_record_queue_name']
        self.generator_to_user_map_name = kwargs['generator_user_map_name']


    def get_transformed_record_queue(self, pipeline_id):
        key = redisx.compose_key(pipeline_id, self.transformed_record_queue_name)
        self.log.info('generated redis key for transformed record queue: "%s"' % key)
        return redisx.Queue(key, self.redis_server)


    def get_raw_record_queue(self, pipeline_id):
        key = redisx.compose_key(pipeline_id, self.raw_record_queue_name)
        self.log.info('generated redis key for raw record queue: "%s"' % key)
        return redisx.Queue(key, self.redis_server)


    def get_generator_to_user_map(self, pipeline_id):
        key = redisx.compose_key(pipeline_id, self.generator_to_user_map_name)
        self.log.info('generated redis key for generator-to-user map: "%s"' % key)
        return redisx.Hashtable(key, self.redis_server)
