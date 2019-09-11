#coding: utf8
from __future__ import absolute_import
import os
import re

interfaces_config_filepath = '/etc/network/interfaces'


def is_a_ip(ip):
    ip = ip.strip()
    if re.match('\d+\.\d+\.\d+\.\d+$', ip):
        return True
    else:
        return False


def get_interfaces_content():
    if not os.path.isfile(interfaces_config_filepath):
        return ''
    with open(interfaces_config_filepath, 'rb') as f:
        config_content = f.read()
    return config_content


def get_interfaces_config():
    config_content = get_interfaces_content()
    if not config_content:
        return {}
    config_r = re.search('iface [^\n]*? inet static.*?gateway.*?($|\n)', config_content, flags=re.S)
    if not config_r:
        return {}
    ip_config_content = config_r.group()
    if 'netmask ' in  ip_config_content:
        netmask_config_content = ip_config_content
    else:
        if 'netmask' not in config_content:
            return {}
        netmask_config_content = config_content
    interface_name = re.search('iface (.*?) inet', ip_config_content).group(1).strip()
    gateway = re.search('gateway.*?(\S+)', config_content).group(1).strip()
    netmask = re.search('netmask.*?(\S+)', netmask_config_content).group(1).strip()
    info = dict(
        name = interface_name,
        gateway = gateway,
        netmask = netmask
    )
    return info



def get_ip_config_content(ip):
    interfaces_config = get_interfaces_config()
    if not interfaces_config:
        return ''
    ip = ip.strip()
    ip_last_part = ip.split('.')[-1]
    name = interfaces_config['name']
    name = '%s:%s' % (name, ip_last_part)
    netmask = interfaces_config['netmask']
    old_config_content = get_interfaces_content()
    if ip in old_config_content:
        return ''
    config_content = '\nauto %s\niface %s inet static\n\taddress %s\n\tnetmask %s\n' % (name, name, ip, netmask)
    return config_content


def write_to_interfaces_config(ip_config_content):
    if not ip_config_content:
        return
    config_content = get_interfaces_content()
    config_content += '\n\n\n%s'%ip_config_content
    with open(interfaces_config_filepath, 'wb') as f:
        f.write(config_content)




def add_new_ip(ip):
    ip = ip.strip()
    if not is_a_ip(ip):
        print('ip format error')
        return
    ip_config_content = get_ip_config_content(ip)
    if not ip_config_content:
        print('no need to add it')
        return
    write_to_interfaces_config(ip_config_content)
    print(get_interfaces_content())
    start_ip(ip)




def start_ip(ip):
    interfaces_content = get_interfaces_content()
    if ip not in interfaces_content:
        print('no ip matched')
        return
    ip_last_part = ip.split('.')[-1]
    interfaces_config = get_interfaces_config()
    name = interfaces_config['name']
    name = '%s:%s' % (name, ip_last_part)
    cmd = 'sudo /sbin/ifup %s' % name
    f = os.popen(cmd)
    f.close()

def stop_ip(ip):
    interfaces_content = get_interfaces_content()
    if ip not in interfaces_content:
        print('no ip matched')
        return
    ip_last_part = ip.split('.')[-1]
    interfaces_config = get_interfaces_config()
    name = interfaces_config['name']
    name = '%s:%s' % (name, ip_last_part)
    cmd = 'sudo /sbin/ifdown %s' % name
    f = os.popen(cmd)
    f.close()




