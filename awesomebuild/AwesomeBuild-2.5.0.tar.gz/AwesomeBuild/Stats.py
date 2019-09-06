#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import json

from weasyprint import HTML, CSS

from .RunStat import RunStat


class Stats:
    def __init__(self, statusfile):
        self.statusfile = statusfile
        self.stats = {}
        for n, sl in statusfile.getStats().items():
            self.stats[n] = [RunStat(s) for s in sl]
        self.totstats = {}

    def save(self):
        self.statusfile.setStats(
            dict(
                [
                    (
                        n, [
                            s.toJSON()
                            for s in sl
                        ]
                    )
                    for n, sl
                    in self.stats.items()
                ]
            )
        )

    def getRun(self, name):
        if name not in self.stats:
            self.stats[name] = []
        rs = RunStat()
        self.stats[name].append(rs)
        return(rs)

    def reset(self):
        self.stats = {}

    def genTotStats(self):
        self.totstats = {}
        for n, d in self.stats.items():
            self.totstats[n] = {}
            stages = []
            for s in d:
                stages += s.times.keys()
            stages = list(set(stages))
            for s in stages:
                vals = []
                for r in d:
                    if s in r.times:
                        vals.append(r.times[s])
                self.totstats[n][s] = {
                    'min': min(vals),
                    'max': max(vals),
                    'avg': sum(vals)/len(vals)
                }

    def savePDF(self, path):
        HTML(
            string=self.genHTML()
        ).write_pdf(
            path,
            stylesheets=[
                CSS(
                    string='''
                            th, td {
                                text-align: center;
                            }
                            table, th, td {
                                border: 1px solid black;
                                border-collapse: collapse;
                            }
                            '''
                )
            ]
        )

    def genHTML(self):
        self.genTotStats()
        header = '<table style="width:100%">'
        footer = '</table>'
        rowopen = '<tr>'
        rowclose = '</tr>'

        def headercellopen(x=1, y=1):
            return(
                '<th' +
                ('' if x == 1 else ' colspan="' + str(x) + '"') +
                ('' if y == 1 else ' rowspan="' + str(y) + '"') +
                '>'
            )
        headercellclose = '</th>'

        def cellopen(x=1, y=1):
            return(
                '<td' +
                ('' if x == 1 else ' colspan="' + str(x) + '"') +
                ('' if y == 1 else ' rowspan="' + str(y) + '"') +
                '>'
            )
        cellclose = '</td>'

        def headercell(v, x=1, y=1):
            return(headercellopen(x, y) + v + headercellclose)

        def cell(v, x=1, y=1):
            return(cellopen(x, y) + v + cellclose)
        rows = []
        rows.append(headercell('Rule', y=2) +
                    headercell('Stage', y=2) + headercell('Times', x=3))
        rows.append(headercell('Min') + headercell('Avg') + headercell('Max'))
        for n, d in [(n, self.totstats[n]) for n in sorted(self.totstats.keys())]:
            stages = [
                s
                for s in [
                    'check-call-before',
                    'check-call-before',
                    'check-triggers',
                    'execute-commands',
                    'save-status',
                    'save-run-before-status',
                    'call-after',
                    'save-triggers'
                ]
                if s in d
            ]
            first = True
            for s in stages:
                sd = d[s]
                rows.append(
                    (cell(n, y=len(stages)) if first else '') +
                    cell(s) +
                    cell('{:.3f}'.format(sd['min'])+'s') +
                    cell('{:.3f}'.format(sd['avg'])+'s') +
                    cell('{:.3f}'.format(sd['max'])+'s')
                )
                first = False
        data = []
        data.append(header)
        for r in rows:
            data.append(rowopen)
            data.append(r)
            data.append(rowclose)
        data.append(footer)
        return(''.join(data))
