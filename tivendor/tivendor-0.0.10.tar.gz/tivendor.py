import datetime
import time
import json
import logging
from _thread import start_new_thread
from urllib.parse import urlparse

import requests
from kafka import KafkaProducer


try:
    requests.packages.urllib3.disable_warnings()
    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNull'
except Exception as e:
    print(e)


class TiVendorError(Exception):
    pass


class EasyCache:
    
    # data = {}
    
    def __init__(self):
        self.data = {}
    
    def set(self, key, value, ttl=300):
        ts = time.time() + ttl
        self.data[key] = (value, ts)
    
    def get(self, key, default=None):
        if key not in self.data:
            return default
        
        value, ts = self.data[key]
        if time.time() > ts:
            self.clear(key)
            return default
        
        return value
        
    def clear(self, key):
        if key not in self.data:
            return
        del self.data[key]
        
    def clear_all(self):
        self.data = {}
        
    
class TiVendor:
    
    cache = EasyCache()
    kafka_producers = {}
    
    def __init__(self, config):
        self.tiadmin_host = config['TIADMIN_HOST'] or 'http://tiadmin.kong:8000'
        self.kafka_enable = config.get('KAFKA_ENABLE', 'on')
        self.kafka_host = config.get('KAFKA_HOST') or 'kafka-kafka.kafka:9092'
        self.kafka_topic = config.get('KAFKA_TOPIC') or 'supplier-request'
        self.default_service_name = config.get('DEFAULT_SERVICE_NAME', '')
        self.logger_name = config.get('LOGGER_NAME') or None

        self.logger = logging.getLogger(self.logger_name)
        self.kafka_producer = self.get_singleton_kafka_producer()

    def get_singleton_kafka_producer(self):

        if self.kafka_enable != 'on':
            return None
        
        if not all([self.kafka_host, self.kafka_topic]):
            raise TiVendorError('KAFKA_HOST and KAFKA_TOPIC should be define in config')
        
        kafka_producers = self.__class__.kafka_producers
        
        if self.kafka_host in kafka_producers:
            return kafka_producers[self.kafka_host]

        kafka_producer = KafkaProducer(
            bootstrap_servers=self.kafka_host.split(','),
            # api_version=(0, 11, 0),
        )
        self.logger.info(f'New kafka_producer: {kafka_producer}')
        kafka_producers[self.kafka_host] = kafka_producer
        return kafka_producer

    def get_api_info(self, api_num):
        info = self.cache.get(api_num)
        if info:
            return info
    
        url = self.tiadmin_host + '/supplier/services/'
        r = requests.get(url, params={'api_num': api_num}).json()
        results = r.get('results')
        if not results:
            raise TiVendorError(f'{api_num} api not found')
    
        info = results[0]
        self.cache.set(api_num, info, ttl=300)
    
        return info

    def request(self, api_num, service_name='', ti_request_headers=None, verify=False, **kwargs):
        info = self.get_api_info(api_num)
        url = info['url']
        method = info['method']
        
        self.logger.info(f'Vendor Request: {method}, {url}, {kwargs}')
        
        start_time = self.now_time()
        response = requests.request(method, url, timeout=60, verify=verify, **kwargs)
        end_time = self.now_time()
    
        if self.kafka_producer:
            
            service_name = service_name or self.default_service_name or self.get_service_name()
            ti_request_headers = ti_request_headers or self.get_ti_request_headers()
            kwargs.update({
                'instance': self,
                'api_info': info,
                'url': url,
                'method': method,
                'response': response,
                'start_time': start_time,
                'end_time': end_time,
                'ti_request_headers': ti_request_headers,
                'service_name': service_name,
            })
            
            start_new_thread(kafka_push, args=(), kwargs=kwargs)
    
        return response
    
    def get_service_name(self):
        try:
            from flask import request
            path = request.path.strip('/')
            service_name = path.split('/')[1]
            return service_name
        except ImportError:
            pass
        # todo: support for more framework
        return ''
    
    def get_ti_request_headers(self):
        try:
            from flask import request
            return dict(request.headers)
        except ImportError:
            pass
        # todo: support for more framework
        return {}

    def now_time(self):
        return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def kafka_push(**kwargs):
    
    instance = kwargs['instance']
    api_info = kwargs['api_info']
    url = kwargs['url']
    method = kwargs['method']
    response = kwargs['response']
    start_time = kwargs['start_time']
    end_time = kwargs['end_time']
    ti_request_headers = kwargs['ti_request_headers']
    service_name = kwargs['service_name']

    url_parse = urlparse(url)
    assert isinstance(instance, TiVendor)

    request_body = kwargs.get('json', '') or kwargs.get('data', '') or kwargs.get('files', '')

    body = {
        'start_time': start_time,
        'end_time': end_time,
        'kong_request_id': ti_request_headers.get('Kong-Request-Id', ''),
        'x_request_id': ti_request_headers.get('X-Request-Id', ''),
        'x_real_ip': ti_request_headers.get('X-Real-Ip', ''),
        'x_consumer_id': ti_request_headers.get('X-Consumer-Id', ''),
        'x_consumer_username': ti_request_headers.get('X-Consumer-Username', ''),
        'x_credential_username': ti_request_headers.get('X-Credential-Username', ''),
        'triple_url': url,
        'triple_host': '%s:%s' % (url_parse.hostname, url_parse.port) if url_parse.port else url_parse.hostname,
        'method': method,
        'request': {
            'headers': json.dumps(dict(response.request.headers)),
            'params': json.dumps(kwargs.get('params', '')),
            'body': json.dumps(request_body) if isinstance(request_body,dict) else request_body,
        },
        'response': {
            'headers': json.dumps(dict(response.headers)),
            'body': response.text,
        },
        'status_code': response.status_code,
        'service_name': service_name,
        'api_num': api_info.get('api_num', ''),
        'supplier_name': '%s-%s-%s' % (
            api_info.get('org_name', 'empty'), api_info.get('product_name', 'empty'),
            api_info.get('product_defines', 'empty')),
    }
    
    try:
        msg = json.dumps(body).encode('utf8')
        instance.kafka_producer.send(instance.kafka_topic, value=msg)
    except:
        instance.logger.error('kafka send error(%s)' % body['kong_request_id'], exc_info=True)

