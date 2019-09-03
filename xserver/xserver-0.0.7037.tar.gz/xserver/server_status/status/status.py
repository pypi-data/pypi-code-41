#coding: utf8
#author: hepochen@gmail.com
from __future__ import absolute_import
import psutil, os, datetime
from .utils import get_ports_opened, capacity_info_to_dict, datetime_to_str
from .usage import get_io_usage, get_net_usage, get_processes_usage


def get_system_status(includes_processes=True, mini=True):
    now = datetime.datetime.utcnow()
    now_s = datetime_to_str(now)
    info = dict(date=now_s)
    cpu_info = dict(
        cores = psutil.cpu_count(),
        logical_cores = psutil.cpu_count(logical=True),
        used = psutil.cpu_percent(interval=1)
    )
    if hasattr(psutil, 'cpu_freq'):
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            cpu_info['current_freq'] = cpu_freq.current
            cpu_info['max_freq'] = cpu_freq.max
        else:
            cpu_info['current_freq'] = '?'
            cpu_info['max_freq'] = '?'
    info['cpu'] = cpu_info

    try:
        load_avg = os.getloadavg() # 1, 5, and 15 minutes
        info['load'] = load_avg[0]
        load_info = {
            'load_1': load_avg[0],
            'load_5': load_avg[1],
            'load_15': load_avg[2],
        }
        info['load_info'] = load_info
    except:
        info['load'] = -1
        info['load_info'] = {}


    mem_info = psutil.virtual_memory()
    info['mem'] = capacity_info_to_dict(mem_info)

    if not mini:
        info['swap_mem'] = capacity_info_to_dict(psutil.swap_memory())

    try:
        info['disk'] = capacity_info_to_dict(psutil.disk_usage('/etc/hosts')) # for docker, get real disk information
    except:
        info['disk'] = capacity_info_to_dict(psutil.disk_usage('/'))

    info['ports'] = get_ports_opened()

    info['net'] = get_net_usage()

    info['io'] = get_io_usage()

    if includes_processes:
        info['processes'] = get_processes_usage(mini=True)

    if mini:
        # 对内容的再组织
        mem_info = info.pop('mem', {})
        new_mem_info = dict(
            total = mem_info.get('total_for_human'),
            used = mem_info.get('used_for_human'),
            used_n = mem_info.get('used') or 0,
            total_n = mem_info.get('total') or 0,
        )
        info['mem'] = new_mem_info



    return info

