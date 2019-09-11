#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import time
from datetime import datetime
from log import logger
import urllib
import socket
import os
import ConfigParser

socket.setdefaulttimeout(10)
def getcurrenttime(segmenter):
    param = "%Y-%m-%d %H-%M-%S"
    para = param.replace("-", segmenter)
    localtime = time.strftime(para, time.localtime())
    logger.info(" The formatted time is "+localtime)
    return localtime

def gettimestamp():
    # 获取当前时间
    times = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(" current time "+times)
    # 转为时间数组
    timearray = time.strptime(times, "%Y-%m-%d %H:%M:%S")
    # 转为时间戳
    timestamp = int(time.mktime(timearray))
    logger.info(" The current timestamp is " + timestamp)
    return timestamp

def getconfig(path):
    cf = ConfigParser.ConfigParser()
    cf.read(path)
    return cf


class basic():
    def __init__(self, host, port):
       self.host = host
       self.port = port
    def get(self, url, params):
        params = urllib.quote(params)  # 将参数转为url编码字符串
        url = 'http://' + self.host + ':' + str(self.port) + url + params
        try:
            response = urllib.urlopen(url)
            response = response.read().decode('utf-8')  ## decode函数对获取的字节数据进行解码
            json_response = json.loads(response)  # 将返回数据转为json格式的数据
            return json_response
        except Exception as e:
            logger.info('%s' % e)
            return {}

    def post(self, url, data):
        data = json.dumps(data)
        data = data.encode('utf-8')
        url = 'http://' + self.host + ':' + str(self.port) + url
        try:
            response = urllib.urlopen(url, data)
            response = response.read().decode('utf-8')
            json_response = json.loads(response)
            return json_response
        except Exception as e:
            logger.info('%s' % e)
            return {}
