#coding: utf8
#author: hepochen@gmail.com
from __future__ import absolute_import
import os, re
from datetime import timedelta


def bytes2human(num):
    if not num:
        return '0'
    for x in ['bytes', 'KB', 'MB', 'GB', 'PB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')



def capacity_info_to_dict(pu_info, capacity_fields=None):
    # turn capacity (dict/mem) into a py-dict type
    default_capacity_fields  = ['total', 'available', 'used', 'free', 'active',
                                'inactive', 'buffers', 'shared', 'cached', 'data', 'vms', 'rss', 'text', 'dirty', 'lib']
    capacity_fields = capacity_fields or default_capacity_fields
    data = {}
    for field in pu_info._fields:
        value = getattr(pu_info, field, None)
        if hasattr(value, '__call__'):
            continue
        if value is None:
            continue
        if field in capacity_fields and isinstance(value, (int, long)):
            human_value = bytes2human(value)
            data['%s_for_human'%field] = human_value
        data[field] = value
    return data




def get_port_info(port):
    try:
        port = int(port)
    except:
        return []
    ports = get_ports_opened()
    return ports.get(port) or []



def get_ports_opened():
    # get all ports opened (as service)
    c_f = os.popen("ss -ln | grep '*:'")
    cmd_content = c_f.read().strip()
    cmd_content_lines = cmd_content.split('\n')
    ports = {}
    for line in cmd_content_lines:
        line = line.strip()
        if 'LISTEN' not in line:
            continue
        parts = re.split('\s+', line)
        address = parts[-2]
        if ':' not in address:
            continue
        port = address.split(':')[-1]
        ip = address.split(':')[0]
        ports.setdefault(port, []).append(ip)
    return ports



def is_process_working(name):
    if '[' in name:
         # transfer, like bellow
         # gunicorn: worker [farbox] -> gunicorn: worker \[farbox\]
        web_c_f = os.popen("ps aux | grep '%s'" % name.replace('[', '\[').replace(']', '\]'))
    else:
        web_c_f = os.popen('ps -C %s -o pid --no-headers' % name)
    try:
        result = web_c_f.read().strip()
        lines = result.split('\n')
        count = len(lines) # count of processes
        #logging.info(result)
        if not result:
            return False
        else:
            return count # return the count of processes
    except:
        return False



def datetime_to_str(date):
    try:
        utc_offset = float(os.environ.get('utc_offset'))
    except:
        utc_offset = 0
    if utc_offset:
        diff = timedelta(hours=utc_offset)
        date += diff
    date_string = date.strftime('%Y-%m-%d %H:%M:%S')
    return date_string
