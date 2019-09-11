#!/usr/bin/python
# -*- coding: UTF-8 -*-
import ConfigParser
import os
from txInterface import basic
from txInterface.log import logger

def getPath(wpath,name):
    proDir = '/home/tx-deepocean/Downloads/autotest'
    path = os.path.join(proDir, "test_data", 'config.ini')
    cf = basic.getconfig(path)
    value = cf.get(wpath, name)
    excel_path = os.path.join(proDir, "test_data", value)
    return excel_path

def getiport(wpath,name):
    result = getPath(wpath,name)
    params = result.split("/")
    logger.info(params[params.__len__()-1])
    return params[params.__len__()-1]

def dirpath():
    proDir = '/home/tx-deepocean/Downloads/autotest'
    path = os.path.join(proDir, "test_data", 'config.ini')
    return path
def modifyValues(ip,port):
    path = dirpath();
    fixConfig = ConfigParser.ConfigParser()
    fixConfig.read(path)
    fixConfig.set("message", "ip", ip)
    fixConfig.set("message", "port", port)
    fixConfig.write(open(path, "r+"))  # 可以把r+改成其他方式，看看结果:)

if __name__ == '__main__':
    modifyValues()