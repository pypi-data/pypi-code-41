#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import hashlib
import json

statusversion = 6


class StatusFile:
    def __init__(self, path, config):
        self.path = path
        self.data = {}
        self.config = config
        self.load()
        self.checkversion()
        self.checkConfigStatus()

    def load(self):
        try:
            with open(self.path) as json_file:
                self.data = json.load(json_file)
        except Exception:
            self.initialize()

    def save(self):
        with open(self.path, 'w') as json_file:
            json.dump(self.data, json_file, indent=4, sort_keys=True)

    def checkversion(self):
        if 'awesomestatusversion' not in self.data:
            # error
            self.initialize()
        elif self.data['awesomestatusversion'] > statusversion:
            # too new
            self.initialize()
        elif self.data['awesomestatusversion'] < statusversion:
            # outdated
            if self.data['awesomestatusversion'] == 1:
                self.data['configstatus'] = ''
                self.data['awesomestatusversion'] = 2
            if self.data['awesomestatusversion'] == 2:
                self.data['rules'] = {}
                self.data['awesomestatusversion'] = 3
            if self.data['awesomestatusversion'] == 3:
                self.data['triggers'] = self.data.pop('trigger')
                self.data['awesomestatusversion'] = 4
            if self.data['awesomestatusversion'] == 4:
                self.data['rules-callBefore'] = {}
                self.data['awesomestatusversion'] = 5
            if self.data['awesomestatusversion'] == 5:
                self.data['stats'] = {}
                self.data['awesomestatusversion'] = 6

    def initialize(self):
        self.data = {
            'awesomestatusversion': statusversion,
            'configstatus': '',
            'triggers': {},
            'rules': {},
            'rules-callBefore': {},
            'stats': {}
        }

    def checkConfigStatus(self):
        if self.data['configstatus'] != self.getConfigHash():
            self.resetStatus()
            self.data['configstatus'] = self.getConfigHash()

    def getConfigHash(self):
        return(
            hashlib.sha512(
                json.dumps(self.config, sort_keys=True)
                .encode()
            ).hexdigest()
        )

    def resetStatus(self):
        self.data['triggers'] = {}
        self.data['rules'] = {}
        self.data['rules-callBefore'] = {}

    def getTrigger(self, key):
        if key in self.data['triggers']:
            return(self.data['triggers'][key])
        return(None)

    def setTrigger(self, key, value):
        self.data['triggers'][key] = value

    def getRule(self, key):
        if key in self.data['rules']:
            return(self.data['rules'][key])
        return(None)

    def setRule(self, key, value):
        self.data['rules'][key] = hashlib.sha512(
            str(value)
            .encode()
        ).hexdigest()

    def getRuleCallBefore(self, key):
        if key in self.data['rules-callBefore']:
            return(self.data['rules-callBefore'][key])
        return(None)

    def setRuleCallBefore(self, key, value):
        self.data['rules-callBefore'][key] = value

    def checkRuleCallBefore(self, rule, callBefore):
        return(
            self.getRuleCallBefore(rule) != self.getMultiRuleHash(callBefore)
        )

    def saveRuleCallBefore(self, rule, callBefore):
        self.setRuleCallBefore(rule, self.getMultiRuleHash(callBefore))

    def getMultiRuleHash(self, rules):
        raw = ''
        for r in rules:
            rh = self.getRule(r)
            if rh is None:
                return(None)
            raw += rh
        return(
            hashlib.sha512(
                raw
                .encode()
            ).hexdigest()
        )

    def getStats(self):
        return(self.data['stats'])

    def setStats(self, stats):
        self.data['stats'] = stats
