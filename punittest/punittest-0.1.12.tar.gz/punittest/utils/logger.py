#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ..settings import Settings
from logging import FileHandler
from io import StringIO
import logging
import time
import os


class Logger:

    def __init__(self, logger_name="punittest",
                 logger_dir=Settings.LOG_DIR,
                 console_level=Settings.LOG_CONSOLE_LEVEL,
                 file_level=Settings.LOG_FILE_LEVEL,
                 report_level=Settings.LOG_REPORT_LEVEL):
        """
        :param logger_dir: 日志文件所在目录路径
        :param logger_name: logger名称
        :param console_level: 控制台输出级别
        :param file_level: 文件输出级别
        :param report_level: 报告输出级别
        """
        self.logger = logging.getLogger(logger_name)
        # 将Log放入StringIO，最后由HTMLTestRunner读取
        self.logger.log_capture = StringIO()
        self.logger.log_file_name = None
        self.logger_dir = logger_dir
        logging.root.setLevel(logging.NOTSET)
        self.formatter = logging.Formatter(
            # '[%(asctime)s][%(levelname)s][%(module)s][%(funcName)s][%(lineno)d]: %(message)s')
            '[%(asctime)s][%(levelname)s]: %(message)s')
        self.console_output_level = console_level
        self.file_output_level = file_level
        self.report_output_level = report_level
        self.backup_count = 20

    def add_handlers(self, console_switch=Settings.LOG_CONSOLE_SWITCH,
                   file_switch=Settings.LOG_FILE_SWITCH,
                   report_switch=Settings.LOG_REPORT_SWITCH):
        """
        在logger中添加日志句柄并返回，如果logger已有句柄，则直接返回
        :param console_switch: 控制台日志开关
        :param file_switch: 文件日志开关
        :param report_switch: 报告日志开关
        :return:
        """
        if console_switch:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.console_output_level)
            console_handler.setFormatter(self.formatter)
            self.logger.addHandler(console_handler)
        if file_switch:
            now_time = time.strftime("%Y-%m-%d_%H-%M-%S")
            self.logger.log_file_name = '{0}.log'.format(now_time)
            if not os.path.exists(self.logger_dir):
                os.makedirs(self.logger_dir)
            log_file_path = os.path.join(self.logger_dir, self.logger.log_file_name)
            file_handler = FileHandler(filename=log_file_path, delay=True, encoding='utf-8')
            file_handler.setLevel(self.file_output_level)
            file_handler.setFormatter(self.formatter)
            self.logger.addHandler(file_handler)
        if report_switch:
            # 将Log放入StringIO，最后由HTMLTestRunner读取
            report_handler = logging.StreamHandler(getattr(self.logger, 'log_capture'))
            report_handler.setLevel(self.report_output_level)
            report_handler.setFormatter(self.formatter)
            self.logger.addHandler(report_handler)
        return self.logger

    def get_logger(self):
        if self.logger.handlers:
            return self.logger
        else:
            return self.add_handlers()

    def get_new_logger(self, console_switch, file_switch, report_switch):
        self.logger.handlers.clear()
        return self.add_handlers(console_switch, file_switch, report_switch)


logger = Logger().get_logger()
