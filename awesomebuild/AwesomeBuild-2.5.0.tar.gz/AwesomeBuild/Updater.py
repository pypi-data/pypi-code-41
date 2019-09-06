#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import json

from .importer import getImportRules, getIndividualImportRulesFileNames


class Updater:
    updaters = {}

    def __init__(self, data, configpath, configdir):
        self.configpath = configpath
        self.configdir = configdir
        self.extfiles = {}
        if 'rules' in self.updaters:
            self.extfiles['rules'] = []
            for ir in getImportRules(data):
                self.extfiles['rules'] += [
                    irf for irf in
                    getIndividualImportRulesFileNames(ir, self.configdir)
                ]
        self.update()

    def update(self):
        self.updateMain()
        self.updateExt()

    def updateMain(self):
        with open(self.configpath) as json_file:
            data = json.load(json_file)
        if 'rules' in self.updaters and 'rules' in data:
            for rn in data['rules'].keys():
                for u in self.updaters['rules']:
                    data['rules'][rn] = u(data['rules'][rn])
        with open(self.configpath, 'w') as json_file:
            json.dump(data, json_file, indent=4, sort_keys=True)

    def updateExt(self):
        self.updateExtRules()

    def updateExtRules(self):
        if 'rules' in self.updaters and 'rules' in self.extfiles:
            for rfn in self.extfiles['rules']:
                with open(rfn) as json_file:
                    data = json.load(json_file)
                for rn in data.keys():
                    for u in self.updaters['rules']:
                        data[rn] = u(data[rn])
                with open(rfn, 'w') as json_file:
                    json.dump(data, json_file, indent=4, sort_keys=True)


def registerUpdater(utype):
    def registerUpdaterDecorator(uf):
        if utype not in Updater.updaters:
            Updater.updaters[utype] = []
        Updater.updaters[utype].append(uf)
    return(registerUpdaterDecorator)


@registerUpdater('rules')
def updaterRulesCallToCmd(data):
    if 'call' in data:
        if isinstance(data['call'], str):
            data['call'] = [data['call']]
        for c in data['call']:
            if 'cmd' not in data:
                data['cmd'] = []
            elif isinstance(data['cmd'], str):
                data['cmd'] = [data['cmd']]
            data['cmd'].append({
                'type': 'rule',
                'rule': c
            })
        del(data['call'])
    return(data)


@registerUpdater('rules')
def updaterRulesCmdExtended(data):
    if 'cmd' in data:
        if isinstance(data['cmd'], str):
            data['cmd'] = [data['cmd']]
        for ci in range(len(data['cmd'])):
            c = data['cmd'][ci]
            if isinstance(c, str):
                c = {
                    'type': 'cmd',
                    'cmd': c
                }
            data['cmd'][ci] = c
    return(data)
