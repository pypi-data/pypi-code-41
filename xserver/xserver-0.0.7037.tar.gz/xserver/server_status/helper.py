#coding: utf8
from __future__ import absolute_import, print_function
from .status.status import get_system_status
import time

def _print_server_status():
    status = get_system_status(includes_processes=False, mini=False)
    print('cpu: %s' % status['cpu']['used'])
    print('mem: %s%%, %s used, %s total' % (status['mem']['percent'], status['mem']['used_for_human'], status['mem']['total_for_human']))
    print('disk: %s%%, %s used, %s total' % (status['disk']['percent'], status['disk']['used_for_human'], status['disk']['total_for_human']))
    print('io: %s%%, read %s/s, write %s/s' % (status['io']['util'], status['io']['read_speed_for_human'], status['io']['write_speed_for_human']))
    print('\n'*3)


def print_server_status(sleep_per_seconds=2, times=3):
    for i in range(times):
        _print_server_status()
        time.sleep(sleep_per_seconds)