# coding: utf-8
from django.http import HttpRequest

from weblogtools.models import InterfaceHistory
import requests
import json
import time

MAX_KEEPING_DATA_LENGTH = 1000


def http_log(server_addr=None, service_name=None, method=None, payload=None, http_status=None,
             http_response_header=None, http_response_content=None, http_error=None, time_it=0):
    """记录http日志"""
    InterfaceHistory.log(
        server_addr, service_name, method, payload, http_status,
        http_response_header, http_response_content, http_error, time_it
    )


def http_log_from_response(service_name, response: requests.Response, timeit=0):
    """调别人通过这里记录日志"""
    request = response.request
    # request = requests.Request()
    body = request.body[:MAX_KEEPING_DATA_LENGTH].decode(errors='ignore')
    http_log(
        request.url, service_name, request.method, body, response.status_code, json.dumps(dict(response.headers)),
        response.content[:MAX_KEEPING_DATA_LENGTH].decode(errors='ignore'), None,
        timeit
    )


def http_log_from_request(service_name, request: HttpRequest, status_code, response_headers,
                          response_content, timeit=0):
    """回调的情况调这里记录日志"""
    body = request.body[:MAX_KEEPING_DATA_LENGTH].decode(errors='ignore')
    http_log(
        request.path, service_name, request.method, body, status_code, json.dumps(dict(response_headers)),
        response_content[:MAX_KEEPING_DATA_LENGTH],
        None, timeit
    )


class TimeIt(object):
    """计时器。

    用法::

        with httplog.TimeIt() as timeit:
            res = requests.post(url, json=payload)
        httplog.http_log_from_response('upload_case', res, timeit.duration)

    """
    def __init__(self):
        self.start = 0
        self.end = 0

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.time()

    @property
    def duration(self):
        return int((self.end - self.start) * 1000)
