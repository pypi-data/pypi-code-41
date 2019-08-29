# -*- coding: utf-8 -*-
import logging

class Logger():

    # def __init__(self, logname, loglevel, logger):
    def __init__(self, logger):
        # '''           指定保存日志的文件路径，日志级别，以及调用文件
        #    将日志存入到指定的文件中
        # '''

        # 创建一个logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.INFO)

        # # 创建一个handler，用于写入日志文件
        # fh = logging.FileHandler(logname)
        # fh.setLevel(logging.DEBUG)

        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # 定义handler的输出格式
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s][%(message)s]')
        # formatter = format_dict[int(loglevel)]
        # fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        # self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def getlogger(self):
        return self.logger