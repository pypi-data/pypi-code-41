# -*- coding: utf-8 -*-

import os
import threading
import time


class ResourceFlowCounter:
    def __init__(self, cfg):
        self.cfg = cfg
        self.current_slice = ResourceFlowSlice()
        self.history_slice = []

    def switch_period(self):
        self.current_slice.time_end = float(time.time())
        self.history_slice.append(self.current_slice)
        self.current_slice = ResourceFlowSlice()


class ResourceFlowCfg:
    namespace = ""
    resource = ""
    category = ""
    dimension1 = ""
    dimension2 = ""
    dimension3 = ""
    dimension4 = ""
    dimension5 = ""
    dimension6 = ""
    dimension7 = ""
    stage = ""
    state = ""
    annotate = ""

    def __init__(self, namespace, resource, category, stage, state):
        self.namespace = namespace
        self.resource = resource
        self.category = category
        self.stage = stage
        self.state = state

    def copy(self):
        res = ResourceFlowCfg(self.namespace, self.resource,
                              self.category, self.stage, self.state)
        res.dimension1 = self.dimension1
        res.dimension2 = self.dimension2
        res.dimension3 = self.dimension3
        res.dimension4 = self.dimension4
        res.dimension5 = self.dimension5
        res.dimension6 = self.dimension6
        res.dimension7 = self.dimension7
        res.annotate = self.annotate
        return res

    def to_string(self):
        return self.namespace + "|" + self.resource + "|" + self.category + "|" + self.stage + "|" + self.state + "|" + self.dimension1 + "|" + self.dimension2 + "|" + self.dimension3 + "|" + self.dimension4 + "|" + self.dimension5 + "|" + self.dimension6 + "|" + self.dimension7


class ResourceFlowRecord(ResourceFlowCfg):
    time_start = 0.0
    time_end = 0.0
    value = 0

    def __init__(self, cfg):
        self.namespace = cfg.namespace
        self.resource = cfg.resource
        self.category = cfg.category
        self.dimension1 = cfg.dimension1
        self.dimension2 = cfg.dimension2
        self.dimension3 = cfg.dimension3
        self.dimension4 = cfg.dimension4
        self.dimension5 = cfg.dimension5
        self.dimension6 = cfg.dimension6
        self.dimension7 = cfg.dimension7
        self.stage = cfg.stage
        self.state = cfg.state
        self.annotate = cfg.annotate

    def set_slice(self, slice):
        self.time_start = slice.time_start
        self.time_end = slice.time_end
        self.value = slice.value

    def get_time_start(self):
        return self.time_start

    def get_time_end(self):
        return self.time_end


class ResourceFlowSlice:
    is_upload = False
    time_start = 0.0
    time_end = 0.0
    value = 0

    def __init__(self):
        self.time_start = float(time.time())

    def get_isupload(self):
        return self.is_upload

    def set_isupload(self, is_upload):
        self.is_upload = is_upload


class ResourceFlowUploadParams:
    data = []

    def add_param(self, data):
        self.data.append(data)
