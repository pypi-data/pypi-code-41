#!/usr/bin/env python  
# encoding: utf-8
# description: get local ip address

import time
import socket
import requests, json, re


def get_mac_address():
    import uuid
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:].upper()
    return '%s:%s:%s:%s:%s:%s' % (mac[0:2], mac[2:4], mac[4:6], mac[6:8], mac[8:10], mac[10:])


def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('www.baidu.com', 0))
        except:
            s.connect(('192.168.0.1', 0))
        ip = s.getsockname()[0]
    except:
        ip = "x.x.x.x"
    finally:
        s.close()
    return ip


def get_extranetip():
    response = requests.get("http://" + str(time.localtime().tm_year) + ".ip138.com/ic.asp")
    ip = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", response.content.decode(errors='ignore')).group(0)
    return ip


# print(get_extranetip())


def postaddress():
    url_json = 'http://192.168.0.160:8095/pc/maker/saveRobotInfo'
    ip = get_ip()
    macaddr = get_mac_address()
    extranetip = get_extranetip()
    data_json = json.dumps({'inIp': ip, 'macAddr': macaddr, 'exIp': extranetip})  # dumps：将python对象解码为json数据
    headers = {'content-type': 'application/json;charset=UTF-8'}
    print(data_json)
    r_json = requests.post(url_json, data_json, headers=headers)
    print(r_json)
    if r_json.status_code == 200:
        return ip
    else:
        time.sleep(5)
        return postaddress()
    # print(r_json.text)
    # print(r_json.content)
