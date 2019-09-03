#coding: utf8
from __future__ import absolute_import
import subprocess
import time
import os

def run_commands(commands, sleep=0):
    if isinstance(commands, (list, tuple)):
        commands = '\n'.join(commands)
    commands = commands.strip()
    for command in commands.split('\n'):
        command = command.strip()
        if command.startswith('#'): continue # just comment
        if not command: continue
        print command+'\n\n'
        subprocess.call(command, shell=True)
        if sleep:
            time.sleep(sleep)

def run(command):
    subprocess.call(command, shell=True)



def get_matched_ps(cmd_part):
    result = []
    cmd = 'ps -A u | grep %s' % cmd_part
    grep_cmd = 'grep %s' % cmd_part
    try:
        raw_result = os.popen(cmd).read()
        lines = raw_result.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if 'ps -A u' in line:
                continue
            if grep_cmd in line:
                continue
            result.append(line)
    except:
        pass
    return result
