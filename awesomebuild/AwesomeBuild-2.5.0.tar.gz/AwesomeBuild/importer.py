#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import glob
import json
import os


def importrules(data, configdir):
    importrules = getImportRules(data)
    for ir in importrules:
        irr = {}
        for f in getIndividualImportRulesFileNames(ir, configdir):
            with open(f) as json_file:
                irr.update(json.load(json_file))
        if ir['rules'] == '*':
            data['rules'].update(irr)
        else:
            for irrl in ir['rules']:
                data['rules'][irrl] = irr[irrl]
    return(data)


def getImportRules(data):
    importrules = []
    if 'import' in data:
        if 'rules' in data['import']:
            if isinstance(data['import']['rules'], dict):
                importrules = data['import']['rules']
            else:
                importrules += data['import']['rules']
    return(importrules)


def getIndividualImportRulesFileNames(ir, configdir):
    files = []
    ipath = os.path.abspath(os.path.join(configdir, ir['value']))
    if ir['type'] == 'directory':
        for irf in glob.glob(ipath + '/*.json'):
            files.append(irf)
    if ir['type'] == 'file':
        files.append(ipath)
    return(files)
