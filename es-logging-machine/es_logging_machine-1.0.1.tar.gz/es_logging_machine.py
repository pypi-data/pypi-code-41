# import ConfigParser
import sys
import pytz
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch, helpers
import certifi
import requests
import boto3


bulk_data = []

config = ConfigParser.ConfigParser()
config.read('test.ini')
component_name = config.get('DEFAULT', 'component_name')
index = config.get('DEFAULT', 'index_name')


def secrets_manager(region_name, secret_name):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )
    return get_secret_value_response['SecretString']


def log_message(component_name, index_name, log_data):
    es_data = {}
    es_data['_op_type'] = 'index'
    es_data['_index'] = index_name
    es_data['component_name'] = component_name
    es_data['@timestamp'] = datetime.now(pytz.utc)
    es_data['body'] = log_data
    bulk_data.append(es_data)
    return es_data


def log_to_elasticsearch(component_name, index, log_data, es_username, es_password, es_url):
    # secrets = secrets_manager()
    log_message(component_name, index, "this_data")
    es_session = requests.Session()
    es_session.auth = (es_username, es_password)
    url = es_url
    es_client = Elasticsearch(
        url, timeout=60, ca_certs=certifi.where(), http_auth=es_session.auth)
    res = helpers.bulk(es_client, bulk_data, True)
    print('Successfully indexed ', res[0],
          " documents")
    if res[1] > 0:
        print('Failed to insert documents exiting...')
    return True
