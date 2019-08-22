"""
NeurodataLab LLC 12.04.2019
Created by Andrey Belyaev
"""
import ndlapi._pyproto.api_common_pb2 as capi
import json


class Task:

    def __init__(self, uid, service):
        self.service = service
        self.uid = uid

        self.result_ = None

    def task_id(self):
        return self.uid

    def request(self):
        return capi.TaskInfo(id=self.uid)

    def update_progress(self):
        return self.service.progress(self)

    def total_progress(self):
        return self.update_progress().progress

    def worker_progress(self):
        wp = self.update_progress().component_progress
        d = {}
        for k in wp:
            d[k] = wp[k]
        return d

    def status(self):
        return self.update_progress().status

    def update_result(self):
        if self.result_ is None:
            self.result_ = self.service.result(self)
            if self.result_.status not in [capi.ERROR, capi.DONE]:
                self.result_ = None

    def ok(self):
        return self.result_ is not None and self.result_.status != capi.ERROR

    def error(self):
        self.update_result()
        if self.result_ is not None:
            return self.result_.message
        else:
            return None

    def result(self):
        self.update_result()
        if self.result_ is not None:
            try:
                return json.loads(self.result_.data.decode())
            except:
                return None
        else:
            return None

    def finished(self):
        return self.status() in [capi.DONE, capi.ERROR]

