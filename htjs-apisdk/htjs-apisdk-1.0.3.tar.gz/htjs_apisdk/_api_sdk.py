#!-*- coding:utf-8 -*-

import sys
import six
import six.moves
import hmac
import base64
import hashlib
import uuid
from datetime import datetime


if six.PY2:
    six.moves.reload_module(sys)
    sys.setdefaultencoding('utf-8')


HTJS_API_SDK_VERSION = '1.0.3'


class HtjsApiSdkError(Exception):
    def __init__(self, *a, **kw):
        super(HtjsApiSdkError, self).__init__(*a, **kw)


class HtjsApiSdkClient(object):
    def __init__(self, access_key_id, access_key_secret):
        assert isinstance(access_key_id, six.string_types)
        assert isinstance(access_key_secret, six.string_types)
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret

    def get_signed_headers(self, method, url, headers=None, http_version='1.1'):
        assert isinstance(method, six.string_types)
        method = method.upper()

        assert isinstance(url, six.string_types)
        assert url.lower().startswith('http://') or url.lower().startswith('https://') or url.startswith('/')

        if url.startswith('/'):
            path = url
            host = None
        else:
            pr = six.moves.urllib_parse.urlparse(url)  # type: six.moves.urllib_parse.ParseResult
            host = pr.netloc
            path = '{}?{}'.format(pr.path, pr.query) if pr.query else pr.path

        headers = dict(six.iteritems(headers)) if isinstance(headers, dict) else dict()

        enforce_headers = sorted(['host', 'date', 'x-htjs-ua', 'x-htjs-nonce'])

        sign_headers = dict()
        for (k, v) in six.iteritems(headers):
            k = k.lower()
            if k in enforce_headers:
                sign_headers[k] = v

        if 'host' not in sign_headers and host:
            headers['Host'] = host
            sign_headers['host'] = host

        if 'date' not in sign_headers:
            now = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
            headers['Date'] = now
            sign_headers['date'] = now

        if 'x-htjs-ua' not in sign_headers:
            version = sys.version
            if isinstance(version, six.string_types):
                version = version.replace('\n', ' ')
            else:
                version = 'UNKNOWN'
            ua = 'Python {}, sdk-ver={}'.format(version, HTJS_API_SDK_VERSION)
            headers['x-htjs-ua'] = ua
            sign_headers['x-htjs-ua'] = ua

        if 'x-htjs-nonce' not in sign_headers:
            nonce = '{}'.format(uuid.uuid4())
            headers['x-htjs-nonce'] = nonce
            sign_headers['x-htjs-nonce'] = nonce

        sign_lines = list()
        sign_lines.append('{} {} HTTP/{}'.format(method, path, http_version))
        for k in enforce_headers:
            if k in sign_headers:
                sign_lines.append('{}: {}'.format(k, sign_headers[k]))
            else:
                raise HtjsApiSdkError('缺少必要的HTTP请求头：{}'.format(k))
        sign_str = '\n'.join(sign_lines)

        ak_id = self.access_key_id
        ak_secret = self.access_key_secret

        if not isinstance(sign_str, six.binary_type):
            sign_str = sign_str.encode('utf-8')
        if not isinstance(ak_secret, six.binary_type):
            ak_secret = ak_secret.encode('utf-8')

        sign = base64.b64encode(hmac.new(ak_secret, sign_str, digestmod=hashlib.sha256).digest())

        if isinstance(sign, six.binary_type):
            sign = sign.decode('utf-8')

        auth = ', '.join([
            'hmac username="{}"'.format(ak_id),
            'algorithm="hmac-sha256"',
            'headers="request-line {}"'.format(' '.join(enforce_headers)),
            'signature="{}"'.format(sign),
        ])

        headers['Authorization'] = auth

        return headers
