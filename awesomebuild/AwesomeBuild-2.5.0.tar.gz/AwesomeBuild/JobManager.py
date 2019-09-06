#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import time
import uuid

WAITINTERVAL = 0.1


class JobManager:
    def __init__(self, n):
        self.n = n
        self.available = []
        self.running = []
        self.jobs = []

    def avail(self, n):
        while True:
            if n not in self.available:
                self.available.append(n)
                return
            time.sleep(WAITINTERVAL)

    def unavail(self, n):
        self.available.remove(n)

    def register(self):
        juuid = str(uuid.uuid4())
        self.jobs.append(juuid)
        return(juuid)

    def resume(self, n):
        if n not in self.available:
            raise(ValueError)
        while True:
            if len(self.running) < self.n:
                if n not in self.running:
                    self.running.append(n)
                    return
            time.sleep(WAITINTERVAL)

    def pause(self, n):
        self.running.remove(n)

    def unregister(self, juuid):
        self.jobs.remove(juuid)

    def isRegistered(self, d):
        return(d in self.jobs)
