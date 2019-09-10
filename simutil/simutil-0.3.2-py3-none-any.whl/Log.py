#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Log日志类"""

__author__ = ''

import logging
import datetime
from simutil.Env import Env
import traceback

class Log(object):
    _instance = None

    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(Log, cls).__new__(cls, *args, **kw)
            cls._init(cls._instance)
        return cls._instance

    def debug(self, msg):
        self.logger.debug(self._format(msg))

    def info(self, msg):
        self.logger.info(self._format(msg))

    def warning(self, msg):
        self.logger.warning(self._format(msg))

    def error(self, msg):
        self.logger.error(self._format(msg))

    def critical(self, msg):
        self.logger.critical(self._format(msg))

    def _init(self):
        self.logger = logging.getLogger("logging")
        env = Env()
        formatter = logging.Formatter('%(asctime)s 【%(levelname)s】%(message)s')
        if env('DEBUG') is not None and env('DEBUG').lower() == 'true':                                 # 命令行调试日志
            self.logger.setLevel("DEBUG")
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
        fh = logging.FileHandler(env.storage_path + "{}.log".format(datetime.datetime.now().strftime("%Y%m%d")))
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def _format(self, msg):
        if isinstance(msg, Exception):
            return 'Exception:' + traceback.format_exc()
        else:
            return msg.__str__()

Log = Log()

if __name__ == '__main__':
    # info 日志
    Log.info([123])
    try:
        r = 1 + 'r'
        # raise Exception('123123')
    except Exception as e:
        # print(e.__class__)
        # print(traceback.print_exc())
        Log.info(e)

    # Log.error("1212e13")
    # Log.critical("1212e13")

    # for i in range(3):
    #
    # for i in range(3):
    #
    pass