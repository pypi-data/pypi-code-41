import datetime
import functools
import hashlib
import base64
import sys
import urllib.parse
import urllib.request
import json
import uuid
import argparse
import hmac
import logging
import logging.handlers


config = {
    'access_key': '',
    'secret_key': '',
    'domain': '',
    'base_url': 'https://alidns.aliyuncs.com/'
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger()


class Signature:

    SHA_DIGEST_SIZE = 20
    SHA_BLOCK_SIZE = 64
    SECRET_KEY = ''

    @staticmethod
    def get(query_list):
        if not config.get('secret_key'):
            return bytes()
        string_to_sign = urllib.parse.quote('GET&/&', safe='&') + urllib.parse.quote(urllib.parse.urlencode(
            sorted(query_list))).replace("+", "%20").replace("*", "%2A").replace("%7E", "~")
        return base64.b64encode(
            hmac.new((config['secret_key'] + '&').encode('utf8'), string_to_sign.encode('utf8'), 'sha1').digest()
        )

    @staticmethod
    def hmac_sha1(secret_key, data):
        if len(secret_key) > Signature.SHA_BLOCK_SIZE:
            secret_key = hashlib.sha1(secret_key)
        secret_key = secret_key.ljust(Signature.SHA_BLOCK_SIZE, b'\0')
        p1 = bytearray(i ^ 0x36 for i in secret_key)
        s1 = hashlib.sha1(p1)
        s1.update(data)
        p2 = bytearray(i ^ 0x5c for i in secret_key)
        s2 = hashlib.sha1(p2)
        s2.update(s1.digest())
        return s2.digest()

    @staticmethod
    def signature(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            parameters = func(*args, **kwargs)
            if isinstance(parameters, dict):
                query_list = list(parameters.items())
            elif isinstance(parameters, list):
                query_list = parameters
            else:
                raise ValueError('unknown parameter type')
            query_list.append(('Signature', Signature.get(query_list).decode('utf8')))
            return query_list

        return _wrapper

    @staticmethod
    def get_signature_parameters():
        return {
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureNonce': str(uuid.uuid4()).replace('-', ''),
            'SignatureVersion': 1.0
        }


def base_parameters(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        parameters = func(*args, **kwargs)
        return {
            'Format': 'JSON',
            'Version': '2015-01-09',
            'AccessKeyId': config['access_key'],
            'Timestamp': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            **Signature.get_signature_parameters(),
            **parameters
        }

    return _wrapper


def make_url(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        parameters = func(*args, **kwargs)
        return config['base_url'] + '?' + urllib.parse.urlencode(parameters)

    return _wrapper


@make_url
@Signature.signature
@base_parameters
def query_domain_url(domain, host_record='@', record_type='A'):
    return {
        'Action': 'DescribeDomainRecords',
        'DomainName': domain,
        'RRKeyWord': host_record,
        'Type': record_type
    }


@make_url
@Signature.signature
@base_parameters
def update_domain_url(record_id, record_value, host_record='@', record_type='A', line='default', ttl=600, **kwargs):
    return {
        'Action': 'UpdateDomainRecord',
        'RR': host_record,
        'RecordId': record_id,
        'Type': record_type,
        'Value': record_value,
        'Line': line,
        'TTL': ttl
    }


def query_domain_record(domain, host_record='@', record_type='A'):
    domain_info = json.loads(urllib.request.urlopen(query_domain_url(domain, host_record, record_type))
                             .read().decode('utf8'))
    records = domain_info.get('DomainRecords', {}).get('Record', [])
    if not records or not records[0].get('RecordId'):
        raise ValueError('record not found')
    return records[0]['RecordId'], records[0]['Value']


def update_domain_record(domain, host_record='@', record_type='A', *args, **kwargs):
    public_ip = urllib.request.urlopen('https://api.ipify.org/').read().decode()
    if not public_ip:
        raise ValueError('public ip not found')
    current_record_id, current_record_value = query_domain_record(domain, host_record, record_type)
    if current_record_value == public_ip:
        return
    update_url = update_domain_url(current_record_id, public_ip, host_record, record_type, *args, **kwargs)
    logger.info(f'Updating \'{public_ip}\' for \'{domain}\': {update_url}')
    response = urllib.request.urlopen(update_url)
    if response.code != 200:
        raise ValueError(f'fail to update record \'{public_ip}\' for \'{domain}\'')


def main():
    parser = argparse.ArgumentParser(description='Aliyun DDNS Client', add_help=True)
    parser.add_argument('-c', dest='config', help='config file path (ignore other arguments)')
    parser.add_argument('--access-key', dest='access_key', help='access Key Id')
    parser.add_argument('--secret-key', dest='secret_key', help='secret Key')
    parser.add_argument('--domain', dest='domain', help='domain name')
    parser.add_argument('--host-record', dest='host_record', help='host record')
    parser.add_argument('--line', dest='line', help='line <default|telecom|unicom|mobile|oversea|edu|drpeng|btvn>')
    parser.add_argument('--ttl', dest='ttl', help='TTL')
    parser.add_argument('--log-file', dest='log_file', help='log file path')
    arguments = parser.parse_args()
    if arguments.config:
        with open(arguments.config, encoding='utf8') as f:
            config.update(json.load(f))
    else:
        for key, value in arguments.__dict__.items():
            if value:
                config[key] = value
    if config.get('log_file') and len(logger.handlers) < 2:
        file_handler = logging.handlers.RotatingFileHandler(config['log_file'], maxBytes=5 * 1024 * 1024, backupCount=1)
        file_handler.setFormatter(logger.handlers[0].formatter)
        logger.addHandler(file_handler)
    try:
        assert config['access_key'], 'access key not found'
        assert config['secret_key'], 'secret key not found'
        assert config['domain'], 'domain name not found'
        update_domain_record(**config)
    except:
        logger.exception('Error in main')


if __name__ == '__main__':
    main()
