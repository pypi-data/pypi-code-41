#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
from lxml import etree
import logging.handlers
import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler


class logger:

    # 先读取XML文件中的配置数据,这里利用了lxml库来解析XML
    # root = etree.parse(os.path.join(os.path.dirname(__file__), 'config.xml')).getroot()
    # 读取日志文件保存路径
    # logpath = root.find('logpath').text
    # 读取日志文件容量，转换为字节
    logsize = 1024*1024*int(5)
    # 读取日志文件保存个数
    lognum = int(1)
    shijian=time.strftime('%Y%m%d', time.localtime(time.time()))+(sys.argv[0].split('/')[-1].split('.')[0])
    # 日志文件名：由用例脚本的名称，结合日志保存路径，得到日志文件的绝对路径
    logname = os.path.join('logs', shijian)
    TimedRotatingFileHandler(logname, when='D', encoding="utf-8")
    # 初始化logger
    log = logging.getLogger()

    # 日志格式，可以根据需要设置
    fmt = logging.Formatter('[%(asctime)s][%(filename)s][line:%(lineno)d][%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')

    # 日志输出到文件，这里用到了上面获取的日志名称，大小，保存个数
    handle1 = logging.handlers.RotatingFileHandler(logname, maxBytes=logsize, backupCount=lognum)
    handle1.setFormatter(fmt)
    # 同时输出到屏幕，便于实施观察
    handle2 = logging.StreamHandler(stream=sys.stdout)
    handle2.setFormatter(fmt)
    log.addHandler(handle1)
    log.addHandler(handle2)
    # 设置日志基本，这里设置为INFO，表示只有INFO级别及以上的会打印
    log.setLevel(logging.INFO)
    # 日志级别
    @classmethod
    def info(cls, msg):
        cls.log.info(msg)
        return

    @classmethod
    def warning(cls, msg):
        cls.log.warning(msg)
        return

    @classmethod
    def error(cls, msg):
        cls.log.error(msg)
        return

    @classmethod
    def debug(cls, msg):
        cls.log.error(msg)
        return