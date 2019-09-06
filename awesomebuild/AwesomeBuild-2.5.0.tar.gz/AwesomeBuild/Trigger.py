#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import os

from .TriggerStatus import TriggerStatus


class Trigger:
    def __init__(self, triggerconfig, configdir, statusfile):
        self.configdir = configdir
        self.triggerconfig = triggerconfig
        self.value = self.triggerconfig['value']
        self.statusfile = statusfile
        self.eval, self.save, self.ispath = {
            'file': {
                'changed': (
                    self.fileChangedTrigger,
                    self.fileChangedTriggerSave,
                    True
                ),
                'exist': (
                    self.fileExistTrigger,
                    self.nosaver,
                    True
                ),
                'not exist': (
                    self.fileNotExistTrigger,
                    self.nosaver,
                    True
                )
            },
            'directory': {
                'changed': (
                    self.directoryChangedTrigger,
                    self.directoryChangedTriggerSave,
                    True
                ),
                'exist': (
                    self.directoryExistTrigger,
                    self.nosaver,
                    True
                ),
                'not exist': (
                    self.directoryNotExistTrigger,
                    self.nosaver,
                    True
                )
            }
        }[self.triggerconfig['type']][self.triggerconfig['subtype']]
        if self.ispath:
            self.relpath = self.value
            self.abspath = os.path.abspath(
                os.path.join(self.configdir, self.value)
            )
        self.triggerstatus = TriggerStatus(self)

    def fileChangedTrigger(self):
        ts = self.triggerstatus.get()
        if not os.path.isfile(self.abspath):
            return(True)
        cs = self.fileChangedTriggerHashGenerator()
        if ts is None:
            return(True)
        if ts != cs:
            return(True)
        return(False)

    def fileChangedTriggerHashGenerator(self):
        return(os.popen('cat ' + self.abspath + ' | sha512sum').read())

    def fileChangedTriggerSave(self):
        self.triggerstatus.set(self.fileChangedTriggerHashGenerator())

    def fileExistTrigger(self):
        return(os.path.isfile(self.abspath))

    def fileNotExistTrigger(self):
        return(not os.path.isfile(self.abspath))

    def directoryChangedTrigger(self):
        ts = self.triggerstatus.get()
        if not os.path.isdir(self.abspath):
            return(True)
        cs = self.directoryChangedTriggerHashGenerator()
        if ts is None:
            return(True)
        if ts != cs:
            return(True)
        return(False)

    def directoryChangedTriggerHashGenerator(self):
        return(
            os.popen(
                'cd ' + self.configdir
                + '; ls -RlgAGi --time-style=+%s '
                + self.relpath + ' | sha512sum'
            ).read()
        )

    def directoryChangedTriggerSave(self):
        self.triggerstatus.set(self.directoryChangedTriggerHashGenerator())

    def directoryExistTrigger(self):
        return(os.path.isdir(self.abspath))

    def directoryNotExistTrigger(self):
        return(not os.path.isdir(self.abspath))

    def nosaver(self):
        pass
