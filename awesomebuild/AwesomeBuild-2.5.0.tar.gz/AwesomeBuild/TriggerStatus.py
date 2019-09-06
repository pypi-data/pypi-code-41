#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#


class TriggerStatus:
    def __init__(self, trigger):
        self.configdir = trigger.configdir
        self.statusfile = trigger.statusfile
        self.value = None
        if trigger.ispath:
            self.key = trigger.relpath

    def get(self):
        return(self[self.key])

    def set(self, value):
        self[self.key] = value

    def __getitem__(self, key):
        return(self.statusfile.getTrigger(key))

    def __setitem__(self, key, value):
        self.statusfile.setTrigger(key, value)
