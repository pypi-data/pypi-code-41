# -*- coding: utf-8 -*-

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin
import requests
import json
from tpspy.base import ClientBase


class ClientMetrics(ClientBase):
    def __init__(self, sys_id=None, sys_secret=None, tps_base_url=None):
        super(ClientMetrics, self).__init__(sys_id=sys_id, sys_secret=sys_secret, tps_base_url=tps_base_url)

    def metrics_resource_flow_upload(self, data):
        url = urljoin(self.tps_base_url, "api/v1/metrics/resource_flow/upload")

        resp = requests.post(url, data=json.dumps(dict(
            data=data
        )), headers=self.post_headers)
        return self.resp_get_json(resp)

    def metrics_resource_flow_get(self, params):
        url = urljoin(self.tps_base_url, "api/v1/metrics/resource_flow/get")

        resp = requests.get(url, data=json.dumps(params), headers=self.get_headers)
        return self.resp_get_json(resp)

    def metrics_upload(self, data):
        url = urljoin(self.tps_base_url, "api/v1/metrics/metrics/upload")

        resp = requests.post(url, data=json.dumps(dict(
            data=data
        )), headers=self.post_headers)
        return self.resp_get_json(resp)

    def metrics_get(self, params):
        url = urljoin(self.tps_base_url, "api/v1/metrics/metrics/get")

        resp = requests.get(url, data=json.dumps(params), headers=self.get_headers)
        return self.resp_get_json(resp)