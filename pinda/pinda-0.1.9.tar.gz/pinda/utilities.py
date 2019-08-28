"""
utilities.py: pinda utility functions
"""
import subprocess
import os

from .data import database
def available_packages(name=None, version=None):
    result = []
    if name is None:
        target_id = '_'
    elif version is None:
        target_id = name + '_'
    else:
        target_id = name + '_' + str(version)
    ids = [i for i in database]
    ids.sort()
    for id in ids:
        if name is None and version is None:
            result.append(database[id])
        elif version is None:
            if target_id == id[:len(target_id)]:
                result.append(database[id])
        else:
            if target_id == id:
                result.append(database[id])
    return result

def is_available(name, version):
    return len(available_packages(name, version)) == 1

def installed_packages(name=None, version=None):
    available = available_packages(name, version)
    if len(available) == 0:
        return []
    installed = []
    DEVNULL = open(os.devnull, 'w')
    pip = pip_command()
    if pip is None:
        raise RuntimeError('Error - cannot find pip or pip3 command')
    listing = subprocess.check_output('{} list'.format(pip), universal_newlines=True, shell=True, stderr=DEVNULL).split('\n')
    for line in listing:
        words = line.split()
        if len(words) == 2:
            package = words[0]
            version = words[1]
            if version[0] == '(' and version[-1] == ')':
                version = version[1:-1]
            for p in available:
                if p['package'] == package and p['version'] == version:
                    installed.append(p)
    return installed

def is_installed(name, version):
    return len(installed_packages(name, version)) == 1

def docker_installed():
    try:
        result = subprocess.check_output('which docker', shell=True, 
                                          universal_newlines=True, 
                                          stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False

def pip_command():
    try:
        result = subprocess.check_output('which pip', shell=True,
                                         universal_newlines=True,
                                         stderr=subprocess.STDOUT)
        return 'pip'
    except subprocess.CalledProcessError:
        pass
    try:
        result = subprocess.check_output('which pip3', shell=True,
                                         universal_newlines=True,
                                         stderr=subprocess.STDOUT)
        return 'pip3'
    except subprocess.CalledProcessError:
        return None
