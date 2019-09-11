#coding: utf8
from __future__ import absolute_import
import netifaces




# 返回三种数据，所有的 ip 列表，一个 bridge name 对应 ips 的字典，一个 ip 对应 bridge 的字典（考虑到实际应用，不存在一个bridge 对应多个 ip）
def get_local_net_ips_data():
    ips = []
    ips_map = {}
    for name in netifaces.interfaces():
        addrs = netifaces.ifaddresses(name)
        if netifaces.AF_INET in addrs:
            addr_results = addrs[netifaces.AF_INET]
            for addr_result in addr_results:
                ip = addr_result.get('addr')
                if ip and ip not in ips_map and ip not in ['localhost', '127.0.0.1'] and ip.split('.')[0] not in ['172', '192', '10']:
                    ips_map.setdefault(name, []).append(ip)
                    ips.append(ip)
    reversed_ips = {}
    for name, ips_by_name in ips_map.items():
        if ips_by_name and len(ips_by_name) == 1:
            reversed_ips[ips_by_name[0]] = name
    return ips, ips_map, reversed_ips