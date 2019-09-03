#coding: utf8
#author: hepochen@gmail.com
from __future__ import absolute_import
import psutil, time
from operator import itemgetter
from .utils import bytes2human
from .process_status import get_processes_raw_data


def get_diff_value(current, pre, field):
    if hasattr(current, field):
        current_value = getattr(current, field)
    else:
        current_value = current.get(field)
    if hasattr(pre, field):
        pre_value = getattr(pre, field)
    else:
        pre_value = pre.get(field)
    if pre_value is not None and current_value is not None:
        return current_value-pre_value
    else:
        return 0


class Usage(object):
    def __init__(self, raw_data_get_func):
        self.prev = None
        self.prev_ts = None
        self.raw_data_get_func = raw_data_get_func
        self.get()  # initialize self.prev
    def compute(self, current, current_ts):
        # currents is current data, current ts is a timestamp
        return {}
    def get(self):
        # 需要用户自己定义
        current = self.raw_data_get_func()
        current_ts = time.time()
        if self.prev:
            data = self.compute(current, current_ts)
        else:
            data = {}
        self.prev = current
        self.prev_ts = current_ts
        return data




class DiskIopsUsage(Usage):
    def __init__(self):
        Usage.__init__(self, psutil.disk_io_counters)

    def compute(self, current, current_ts):
        time_diff = current_ts - self.prev_ts
        busy_diff = float((current.busy_time - self.prev.busy_time)) / 1000  # ms to seconds
        read_time_diff = float(current.read_time- self.prev.read_time) / 1000
        write_time_diff = float(current.write_time- self.prev.write_time) / 1000
        utilization = (busy_diff / time_diff) * 100.0
        read_utilization = (read_time_diff / time_diff) * 100.0
        write_utilization = (write_time_diff / time_diff) * 100.0
        if utilization < 0:
            utilization = 0
        if read_utilization < 0:
            read_utilization = 0
        if write_utilization < 0:
            write_utilization = 0
        read_bytes_diff = current.read_bytes - self.prev.read_bytes
        read_count_diff = current.read_count - self.prev.read_count
        write_bytes_diff = current.write_bytes - self.prev.write_bytes
        write_count_diff = current.write_count - self.prev.write_count
        read_bytes_per_s = read_bytes_diff / time_diff
        read_count_per_s = read_count_diff / time_diff
        write_bytes_per_s = write_bytes_diff / time_diff
        write_count_per_s = write_count_diff / time_diff
        data = dict(
            util = utilization,
            read_util = read_utilization,
            write_util = write_utilization,
            read_speed = read_bytes_per_s,
            read_speed_for_human = bytes2human(read_bytes_per_s),
            write_speed = write_bytes_per_s,
            write_speed_for_human = bytes2human(write_bytes_per_s),
            read_count_speed = read_count_per_s,
            write_count_speed = write_count_per_s
        )
        return data





def get_net_io_raw_data():
    data = psutil.net_io_counters(pernic=True)
    return data

class NetUsage(Usage):
    def __init__(self):
        Usage.__init__(self, get_net_io_raw_data)
    def compute(self, current, current_ts):
        time_diff = current_ts - self.prev_ts
        net_interfaces = current.keys()
        data = {}
        for net_interface in net_interfaces:
            if 'eth0' in net_interfaces and net_interface != 'eth0':
                continue
            if net_interface in ['lo']:
                continue
            if net_interface.startswith('veth') and len(net_interface) >= 10: # interface from docker, not real
                continue
            if net_interface.startswith('docker'):
                continue
            if net_interface not in self.prev: # 必须也在 prev 中才能对比
                continue
            if net_interface.startswith('lxcbr'):
                continue
            sent = current[net_interface].bytes_sent
            if sent < 1024*10: # 发送的量太少了，可能不是外网 IP, 10k
                continue
            if ':' in net_interface or '.' in net_interface:
                if sent < 1024 * 1024 * 10:
                    continue
            recv = current[net_interface].bytes_recv
            if not sent and not recv: # not working...
                continue
            bytes_sent_diff = sent - self.prev[net_interface].bytes_sent
            bytes_recv_diff = recv - self.prev[net_interface].bytes_recv
            send_speed = bytes_sent_diff / time_diff
            recv_speed = bytes_recv_diff / time_diff
            interface_data = dict(
                sent = sent,
                sent_for_human = bytes2human(sent),
                recv = recv,
                recv_for_human = bytes2human(recv),
                send_speed = send_speed,
                recv_speed = recv_speed,
                send_speed_for_human = bytes2human(send_speed),
                recv_speed_for_human = bytes2human(recv_speed),
                send_speed_m = send_speed/(1024*1024.0), # MB
                recv_speed_m = recv_speed/(1024*1024.0), # MB
            )
            data[net_interface] = interface_data
        return data





class ProcessesUsage(Usage):
    def __init__(self):
        Usage.__init__(self, get_processes_raw_data)
    def compute(self, current, current_ts):
        time_diff = current_ts - self.prev_ts
        processes_info = current
        for pid, process_info in processes_info.items():
            pre_process_info = self.prev.get(pid)
            if not pre_process_info:
                continue
            process_io_info = process_info['io']
            pre_process_io_info = pre_process_info['io']
            read_bytes_diff = get_diff_value(process_io_info, pre_process_io_info, 'read_bytes')
            read_count_diff = get_diff_value(process_io_info, pre_process_io_info, 'read_count')
            write_bytes_diff = get_diff_value(process_io_info, pre_process_io_info, 'write_bytes')
            write_count_diff = get_diff_value(process_io_info, pre_process_io_info, 'write_count')
            read_bytes_per_s = read_bytes_diff / time_diff
            read_count_per_s = read_count_diff / time_diff
            write_bytes_per_s = write_bytes_diff / time_diff
            write_count_per_s = write_count_diff / time_diff
            io_speed_info =  dict(
                read_speed = read_bytes_per_s,
                read_speed_for_human = bytes2human(read_bytes_per_s),
                write_speed = write_bytes_per_s,
                write_speed_for_human = bytes2human(write_bytes_per_s),
                read_count_speed = read_count_per_s,
                write_count_speed = write_count_per_s
            )
            process_io_info.update(io_speed_info)
        return processes_info

    @staticmethod
    def to_mini_data(data):
        mini_data = []
        high_cpu_records = []
        fields = ['pid', 'ppid', 'cpu', 'docker', 'mem_percent', 'ps_mem_percent', 'cmd', 'name', 'created_at']
        for pid, process_info in data.items():
            process_record = {}
            if process_info.get('ppid') == 1: # 系统根进程的, 不显示
                continue
            process_cmd = process_info.get('cmd')
            process_name = process_info.get('name') or ''
            if process_cmd and process_cmd.startswith('docker-'):
                continue
            if process_name in ['docker-proxy', 'supervisord', 'bash']:
                continue
            if process_name.startswith('(') and process_name.endswith(')'):
                continue
            mem_info = process_info.get('mem') or {}
            vms_mem_size = mem_info.get('vms') or ''
            if vms_mem_size < 20*1024*1024: # 小余 20M 占用的内容
                continue

            #if cpu_percent < 0.1:
            #    continue
            for field in fields:
                if field in process_info:
                    v = process_info.get(field)
                    process_record[field] = v
            if mem_info:
                process_record['mem'] = mem_info.get('rss_for_human') # rss_for_human
            io_info = process_info.get('io')
            if io_info:
                process_record['write_bytes'] = io_info.get('write_bytes_for_human')
                process_record['read_bytes'] = io_info.get('read_bytes_for_human')
            mini_data.append(process_record)

            cpu_percent = process_info.get('cpu') or 0

            if cpu_percent > 0.05: # 5% 以上的 cpu 都进行记录
                high_cpu_records.append(process_record)

        # mem 取到 前10 就可以了
        records = sorted(mini_data, key=itemgetter('mem_percent'), reverse=True)
        mini_data = records[:20]
        for record in high_cpu_records:
            if record not in mini_data:
                mini_data.insert(0, record)

        # ppid 对应的在前 10 的, 不管怎样, 都会添加
        added_pids = []
        ppids_to_add = []
        for record in mini_data:
            pid = record.get('pid')
            ppid = record.get('ppid')
            if pid is not None:
                added_pids.append(pid)
            if ppid is not None:
                ppids_to_add.append(ppid)
        ppids_to_add = [pid for pid in ppids_to_add if pid not in added_pids]
        for record in records:
            pid = record.get('pid')
            name = record.get('name')
            if pid is None or name is None:
                continue
            if pid in ppids_to_add and pid not in added_pids:
                mini_data.append(record)
                added_pids.append(pid)
            elif name.startswith('nginx'):
                mini_data.append(record)
                added_pids.append(pid)

        return mini_data

    def get(self, mini=True):
        data = Usage.get(self)
        if not mini:
            return data
        else:
            return self.to_mini_data(data)








############# utils for usage #############

io_usage_obj = None
net_usage_obj = None
processes_usage_obj = None



def get_io_usage():
    global io_usage_obj
    if not io_usage_obj:
        io_usage_obj = DiskIopsUsage()
    return io_usage_obj.get()


def get_net_usage():
    global net_usage_obj
    if not net_usage_obj:
        net_usage_obj = NetUsage()
    return net_usage_obj.get()


def get_processes_usage(mini=False):
    global processes_usage_obj
    if not processes_usage_obj:
        processes_usage_obj = ProcessesUsage()
    return processes_usage_obj.get(mini=mini)







