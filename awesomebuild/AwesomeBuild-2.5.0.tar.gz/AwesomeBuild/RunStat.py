#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import time


class RunStat:
    def __init__(self, json={}):
        self.times = {} if 'times' not in json else json['times']
        self.starttime = None
        self.stage = ""

    def start(self, stage):
        self.stage = stage
        if self.stage not in self.times:
            self.times[self.stage] = 0
        self.starttime = time.time()

    def stop(self):
        stoptime = time.time()
        self.times[self.stage] += (stoptime - self.starttime)

    def toJSON(self):
        return({'times': self.times})
