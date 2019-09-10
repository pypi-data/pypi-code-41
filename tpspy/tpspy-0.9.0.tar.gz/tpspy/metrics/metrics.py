# -*- coding: utf-8 -*-
import threading
import time

from tpspy.metrics.resource_flow import ResourceFlowCounter, ResourceFlowRecord

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin
import requests
import json
from tpspy.base import ClientBase


class ClientMetrics(ClientBase):
    counters = {}
    is_running = False
    switch_period_sec = 60
    cache_history_records = 10

    def __init__(self, sys_id=None, sys_secret=None, tps_base_url=None):
        super(ClientMetrics, self).__init__(sys_id=sys_id, sys_secret=sys_secret, tps_base_url=tps_base_url)

    def metrics_resource_flow_upload(self, data):
        url = urljoin(self.tps_base_url, "api/v1/metrics/resource_flow/upload")
        resp = requests.post(url, data=json.dumps(dict(data=data)), headers=self.post_headers)
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

    # 打点函数
    def metrics_resource_flow_add(self, cfg, n):
        key = cfg.to_string()

        if key not in self.counters:
            counter = ResourceFlowCounter(cfg)
            counter.current_slice.value += n
            self.counters[key] = counter

        else:
            self.counters[key].current_slice.value += n

    def metrics_resource_flow_switch_period(self):
        for (key, counter) in self.counters.items():
            counter.switch_period()
        to_upload_records = []
        for (key, counter) in self.counters.items():
            for s in counter.history_slice:
                if not s.get_isupload():
                    if not s.value == 0:
                        record = ResourceFlowRecord(counter.cfg)
                        record.set_slice(s)
                        to_upload_records.append(record)

                    s.set_isupload(True)

            # clean up
            if len(counter.history_slice) > self.cache_history_records:
                size = len(counter.history_slice)
                counter.history_slice = counter.history_slice[size - self.cache_history_records:size]
        # 上报list
        if len(to_upload_records) > 0:
            data = []
            for record in to_upload_records:
                record_dict = record.__dict__
                data.append(record_dict)
            resp = self.metrics_resource_flow_upload(data)
            print("resp.text: ", resp)

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        sync_thread = self.TimerThread(self)
        sync_thread.start()

    def stop(self):
        self.is_running = False

    # 定时器线程
    class TimerThread(threading.Thread):
        def __init__(self, client):
            threading.Thread.__init__(self)
            self.ClientMetrics = client

        def run(self):
            while True:
                try:
                    if not self.ClientMetrics.is_running:
                        break
                    # 间隔上报
                    time.sleep(self.ClientMetrics.switch_period_sec)
                    self.ClientMetrics.metrics_resource_flow_switch_period()
                except Exception as e:
                    print(e)

    def set_switch_period_sec(self, sec):
        self.switch_period_sec = sec

    def set_cache_history_records(self, size):
        self.cache_history_records = size

    def get_cache_history_records(self):
        return self.cache_history_records

    def get_switch_period_sec(self):
        return self.switch_period_sec
