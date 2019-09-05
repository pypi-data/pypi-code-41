# author: zac
# create-time: 2019-08-15 17:49
# usage: - 

import logging.handlers
import logging
import sys
import time
import datetime
import time


def _formatter(timezone=8):
    #############################################################################
    # converter 处理时区问题
    #   1. __beijing 这个函数很特殊，只能这样写，因为 logging.Formatter.converter
    #      接收参数是一个 有两个参数（sec, what）的function
    #############################################################################
    def __beijing(sec, what):
        beijing_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=timezone))
        return beijing_time.timetuple()

    logging.Formatter.converter = __beijing
    formatstr = '|%(asctime)s| [%(levelname)s] [%(filename)s-%(lineno)d] %(message)s'
    formatter = logging.Formatter(formatstr, "%Y-%m-%d %H:%M:%S")
    return formatter


def get_console_logger(loglevel=logging.DEBUG, loggername=None, timezone=8):
    loggername_ = str(int(time.time())) if loggername is None else loggername
    logger = logging.getLogger(loggername_)
    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(loglevel)
    ch.setFormatter(_formatter(timezone=timezone))
    logger.addHandler(ch)
    return logger


def get_file_logger(info_log_file, err_log_file, min_default_loglevel=logging.INFO, max_default_loglevel=logging.INFO,
                    loggername=None, timezone=8):
    loggername_ = str(int(time.time())) if loggername is None else loggername
    logger = logging.getLogger(loggername_)
    logger.setLevel(logging.DEBUG)

    #########################
    # handler 控制输出目标
    #########################
    fh_default = logging.handlers.TimedRotatingFileHandler(info_log_file, when='D', interval=1, backupCount=15,
                                                           encoding='utf-8')
    fh_err = logging.handlers.TimedRotatingFileHandler(err_log_file, when='D', interval=1, backupCount=15,
                                                       encoding='utf-8')
    #################
    # filter 日志等级
    #################
    filter_default = logging.Filter()
    filter_default.filter = lambda record: min_default_loglevel <= record.levelno <= max_default_loglevel  # 设置过滤等级
    filter_err = logging.Filter()
    filter_err.filter = lambda record: record.levelno == logging.ERROR  # 设置过滤等级

    ######################
    # formatter 规范化输出
    ######################
    fh_default.setFormatter(_formatter(timezone=timezone))
    fh_default.addFilter(filter_default)
    fh_err.setFormatter(_formatter(timezone=timezone))
    fh_err.addFilter(filter_err)

    logger.addHandler(fh_default)
    logger.addHandler(fh_err)
    return logger
