#coding: utf8
#author: hepochen@gmail.com
from __future__ import absolute_import

import psutil, time, datetime, os, re
from .utils import bytes2human, capacity_info_to_dict, datetime_to_str
from .docker_status import get_valid_docker_containers


should_ignored_process_cmds = [
    'upstart-file-bridge',
    'upstart-socket-bridge',
    'rsyslogd',
    'dbus-daemon',
    '/sbin/getty',
    '/usr/sbin/haveged',
    '/usr/sbin/irqbalance',
    '/usr/sbin/sshd',
    '/usr/sbin/ntpd',
    'cron',

]
def should_ignore_process(name, pid, cmd):
    if pid < 500:
        return True
    if name is None:
        return True
    if not cmd:
        return True
    if cmd.startswith('[') and cmd.endswith(']'):
        # from system and for system
        return True
    if cmd.startswith('/lib/systemd/'):
        return True
    if name in ['sshd']:
        return True
    first_part = cmd.split(' ')[0]
    if first_part in should_ignored_process_cmds:
        return True
    return False



def get_all_child_pids(processes_info, pid, pids=None,):
    if pids is None:
        pids = []
    pid_info = processes_info.get(pid) or {}
    children = pid_info.get('children') or []
    for child_pid in children:
        pids.append(child_pid)
        get_all_child_pids(processes_info, child_pid, pids=pids)
    return pids




def get_processes_info_by_ps():
    cmd = 'ps axo pid,%cpu,%mem'
    fp = os.popen(cmd)
    result_list = fp.read().strip().split('\n')[1:]
    fp.close()
    processes_info = {}
    for line in result_list:
        line = line.strip()
        parts = re.split('\s+', line)
        try:
            pid, cpu, mem = parts
            pid = int(pid)
            cpu = float(cpu)
            mem = float(mem)
            processes_info[pid] = dict(cpu=cpu, mem=mem)
        except:
            continue
    return processes_info




def get_processes_raw_data():
    processes_info = {}
    pids = psutil.pids()

    ps_processes_info = get_processes_info_by_ps()
    for pid in pids:
        p = psutil.Process(pid)
        p_name = p.name()
        p_mem_info = capacity_info_to_dict(p.memory_info())
        p_mem_percent = p.memory_percent()
        _cmds = p.cmdline() # like ['/bin/sh', '/etc/init.d/supervisord', 'start']
        cmds = [i for i in _cmds if i]
        ppid = p.ppid() # parent pid
        try:
            raw_io_info = p.io_counters()
            io_info  =  dict(
                read_count = raw_io_info.read_count,
                write_count = raw_io_info.write_count,
                read_bytes = raw_io_info.read_bytes,
                write_bytes = raw_io_info.write_bytes,
                read_bytes_for_human = bytes2human(raw_io_info.read_bytes),
                write_bytes_for_human = bytes2human(raw_io_info.write_bytes),
            )
        except:
            io_info = {}
        ps_pid_info = ps_processes_info.get(pid) or {}
        ps_cpu = ps_pid_info.get('cpu') or 0
        ps_mem = ps_pid_info.get('mem') or 0
        p_info = dict(
            name = p_name,
            pid = pid,
            ppid = ppid,
            mem = p_mem_info,
            mem_percent = p_mem_percent,
            ps_mem_percent = ps_mem,
            cpu = ps_cpu or p.cpu_percent(),
            io = io_info
        )

        try:
            created_at = p.create_time()
            created_at = datetime.datetime.fromtimestamp(created_at)
            created_at = datetime_to_str(created_at)
        except:
            created_at = ''
        p_info['created_at'] = created_at


        if cmds:
            cmd = ' '.join(cmds)
            if 'grin' in cmd and ' -p ' in cmd and 'listen' in cmd:
                cmd = 'grin wallet listen...'
            p_info['cmd'] = cmd
        else:
            cmd = None
        if should_ignore_process(p_name, pid, cmd):
            continue
        processes_info[pid] = p_info
    # get children for pid
    pids_with_children = set()
    for pid, pid_info in processes_info.items():
        ppid = pid_info['ppid']
        parent_pid_info = processes_info.get(ppid)
        if parent_pid_info:
            parent_pid_info.setdefault('children', []).append(pid)
            pids_with_children.add(ppid)
    # dump all children (includes sub-children) into a pid
    for pid in pids_with_children:
        pid_info = processes_info.get(pid)
        if not pid_info:
            continue
        all_children = get_all_child_pids(processes_info, pid) or []
        pid_info['all_children'] = all_children
    # connect with docker container
    docker_containers = get_valid_docker_containers()
    for container_name, container_info in docker_containers.items():
        container_pid = container_info.get('pid')
        container_pid_info = processes_info.get(container_pid)
        if not container_pid_info:
            continue
        container_pid_info['docker'] = container_name
        container_pid_info['docker_root_id'] = True
        container_all_child_pids = container_pid_info.get('all_children') or []
        for child_pid in container_all_child_pids:
            child_pid_info = processes_info.get(child_pid)
            if not child_pid_info:
                continue
            else:
                child_pid_info['docker'] = container_name
    return processes_info


