#! /usr/bin/python

import csv
from datetime import datetime
import os
import sys

import gc3libs
from gc3libs.quantity import Duration, Memory
from gc3libs.session import Session


cwd = os.getcwd()

output = csv.writer(sys.stdout)

# header row
output.writerow([
    'inputfile',
    'funcname',
    'radius',
    'exitcode',
    'cores',
    'requested_memory',
    'used_memory',
    'duration',
    'started_at',
    'terminated_at',
])

for entry in os.listdir(cwd):
    if not entry[0].isupper():
        continue
    session = Session(os.path.join(cwd, entry))
    for task in session:
        # skip unfinished tasks
        if 'TERMINATED' not in task.execution.timestamp:
            continue
        try:
            parts = os.path.basename(task.output_dir).split('_')
            inputfile = parts[-2]
        except ValueError:
            sys.stderr.write("*** ERROR: Malformed jobname `%s` in task %s\n" % (task.output_dir, task))
            continue
        funcname = task.funcname
        radius = task.radius
        cores = task.requested_cores
        req_memory = task.requested_memory.amount(unit=Memory.MB)
        try:
            used_memory = task.execution.max_used_memory.amount(unit=Memory.MB)
        except AttributeError:
            used_memory = req_memory
        exitcode = task.execution._exitcode
        started_at = datetime.utcfromtimestamp(task.execution.timestamp['SUBMITTED'])
        terminated_at = datetime.utcfromtimestamp(task.execution.timestamp['TERMINATED'])
        try:
            duration = task.execution.duration.amount(unit=Duration.s)
        except AttributeError:
            duration = (terminated_at - started_at).total_seconds()
        output.writerow([
            inputfile,
            funcname,
            radius,
            exitcode,
            cores,
            req_memory,
            used_memory,
            duration,
            started_at.isoformat(),
            terminated_at.isoformat(),
        ])
    
