#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import sys
import json
import requests
import traceback
import gzip
import StringIO

from kd_exception import *

from kdbase.log import *

#raise ConnectTimeOutException
def hbase_kv_set(kv_set_url, key, value, namespace, retry_time=3):
    url = '%s?key=%s&namespace=%s' % (kv_set_url, key, namespace)
    logger().info('kv set url:%s', url)
    try:
        ret = requests.post(url, data=value)
        status = ret.status_code
        if status != 200:
            raise ConnectException('hbase_kv_set', status)
        res = ret.json()
        logger().info('save kv namespace[%s], key[%s], '
                'result:%s', namespace, key, res)
        result = res['result']
        if result == False:
            raise ConnectException('hbase_kv_set', status)
    except Exception as e:
        if retry_time == -1:
            raise ConnectTimeOutException('hbase_kv_set', 4)
        err_msg = traceback.format_exc()
        logger().error(err_msg)
        return hbase_kv_set(kv_set_url, key, value, namespace, retry_time - 1)

#raise ConnectTimeOutException
def hbase_kv_get(kv_get_url, key, namespace, retry_time=3):
    url = '%s?key=%s&namespace=%s' % (kv_get_url, key, namespace)
    logger().info('kv get url:%s', url)
    try:
        ret = requests.get(url)
        status = ret.status_code
        content_type = ret.headers['Content-Type']
        assert status == 200
    except Exception as e:
        if retry_time == -1:
            raise ConnectTimeOutException('hbase_kv_get', 4)
        err_msg = traceback.format_exc()
        logger().error(err_msg)
        return hbase_kv_get(kv_get_url, key, namespace, retry_time - 1)
    value = None
    if content_type != 'application/json':
        value = ret.text
        logger().info('get kv namespace[%s] key[%s] result:%s, '
                'Content-Type:%s' % (namespace, key, value[:100], 
                content_type))
        return value
    value = ret.json()
    logger().error('get kv result %s', json.dumps(value))
    if value['code'] == 105:
        raise ValueIsNoneException
    else:
        raise ValueError 

def hbase_kv_gzip_set(kv_set_url, key, value, namespace, retry_time=3):
    out = StringIO.StringIO() 
    with gzip.GzipFile(fileobj=out, mode="w") as f: 
        f.write(value)
    value = out.getvalue()
    url = '%s?key=%s&namespace=%s' % (kv_set_url, key, namespace)
    logger().info('kv set url:%s', url)
    try:
        ret = requests.post(url, data=value)
        status = ret.status_code
        if status != 200:
            raise ConnectException('hbase_kv_gzip_set', status)
        res = ret.json()
        logger().info('save kv namespace[%s], key[%s], '
                'result:%s', namespace, key, res)
        result = res['result']
        if result == False:
            raise ConnectException('hbase_kv_gzip_set', status)
    except Exception as e:
        if retry_time == -1:
            raise ConnectTimeOutException('hbase_kv_gzip_se', 4)
        err_msg = traceback.format_exc()
        logger().error(err_msg)
        return hbase_kv_gzip_set(kv_set_url, key, value, namespace, retry_time - 1)

if __name__ == "__main__":
    pass
    #n = 'recognition_quality'
    #u = 'http://192.168.8.16:9527/test/kv/set/v'
    #u2 = 'http://192.168.8.16:9527/test/kv/set/gzip'
    #url_get = 'http://192.168.8.16:9527/test/kv/get/v2' 
    #v1 ="你好"
    #v2 = "哈哈哈"
    #hbase_kv_set(u, 'test', v1, 'test')
    #print hbase_kv_get(url_get, 'tet', 'test')
    #hbase_kv_gzip_set(u2, 'test', v2, 'test')
    #print hbase_kv_get(url_get, 'test', 'test')

