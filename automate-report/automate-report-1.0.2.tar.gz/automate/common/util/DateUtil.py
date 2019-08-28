#coding=utf-8
__author__ = 'circlq'


import sys

old_sys_path = sys.path
sys.path = sys.path[1:] + sys.path[:1]

import datetime   #对于日期和时间进行简单或复杂的操作
import time as sys_time   # 包含各方面对时间操作的函数

# 获取当前时间戳
now = sys_time.time()
sys.path = old_sys_path


import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(__name__)

DAY_TS = 86400


def get_expire_time(expire_days, begin_time=0):
    """
    计算过期时间，精准到毫秒（13位时间戳）

    :param create_time: 开始时间（时间戳）

    :param expire_days: 有效天数，不可以为0

    .. code-block:: python
        :linenos:

        >>> ts = get_expire_time(1, 0)
        >>> print ts

    """
    if begin_time == 0:
        # 现在的时间戳
        begin_time = int(sys_time.time()) * 1000 + datetime.datetime.now().microsecond/1000

    expires_microsecond = 1000 * 60 * 60 * 24 * int(expire_days)

    expire_time = begin_time + expires_microsecond

    return expire_time


def gen_time_str(t_info):
    """
    从时间信息生成要访问的日志文件名

    20150101

    """
    year = str(t_info.tm_year)

    if t_info.tm_mon < 10:
        month = '0'+str(t_info.tm_mon)
    else:
        month = str(t_info.tm_mon)

    if t_info.tm_mday < 10:
        day = '0'+str(t_info.tm_mday)
    else:
        day = str(t_info.tm_mday)

    return year+month+day


def get_date_ymd():
    """

    :return:

    .. code-block:: python
        :linenos:

        >>> ymd = get_date_ymd()
        >>> print ymd

    """

    now = sys_time.time()

    ltime = sys_time.localtime(now)   #将时间戳转化为UTC 时区的struct_time (世界时间)

    return gen_time_str(ltime)


def info():
    """

    info() -> time_struct

    :return:

    .. code-block:: python
        :linenos:

        >>> time_struct = info()
        >>> print time_struct

    """
    print("time")
    return sys_time.localtime()


def get_ts():
    """
    系统时间戳，整型
    """
    return int(sys_time.time())


def get_log_time():
    """
    返回下划线分割的格式

    .. code-block:: python

        >>> print get_log_time()

    """
    return datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

def utc_time():
    """
    使用UTC时区，方便前端js库进行时间格式化

    .. code-block:: python
        :linenos:

        >>> from setup.auto import utc_time
        >>> print utc_time()

    :return:
    """
    return datetime.datetime.utcnow()


def get_cur_date(fmt="%Y-%m-%d"):
    """

    :param fmt:
    :return:

    .. code-block:: python

        >>> get_cur_date()
        >>> get_cur_date("%Y%m%d")

    """
    return datetime.datetime.now().strftime(fmt)


class CoTime(object):
    def __init__(self, init_day):
        self.ts = 0
        if isinstance(init_day, float) or isinstance(init_day, int):
            # print "浮点型"
            self.ts = int(init_day)
            self.t_info = sys_time.localtime(self.ts)

            # 浮点表示
            self.ts_f = sys_time.mktime(self.t_info)
        elif isinstance(init_day, str):
            # print "字符串"
            # 字符串 -> 时间结构
            self.t_info = sys_time.strptime(init_day, "%Y-%m-%d %H:%M:%S")
            self.ts_f = sys_time.mktime(self.t_info)
            self.ts = int(self.ts_f)

    def get_dt(self):
        return datetime.datetime(self.get_year(), self.get_month(), self.get_day(), 0, 0, 0)

    def get_ts(self):
        return self.ts

    def get_year(self):
        return self.t_info.tm_year

    def get_month(self):
        return self.t_info.tm_mon

    def get_day(self):
        return self.t_info.tm_mday

    def get_weekday(self):
        """
        返回周几
        周一返回1
        """
        return self.t_info.tm_wday + 1

    def get_t_info(self):
        """

        """
        return self.t_info

    def get_format_str(self, f):
        return sys_time.strftime(f, self.t_info)   # strftime()方法格式化当前时间则为（%Y-%m-%d %H:%M:%S')


def dt():
    """
    返回当前时区日期时间对象

    void -> datetime

    :return:

    .. code-block::python

        >>> print dt()
        >>> print type(dt())

    """
    return datetime.datetime.now()

def dt_to_struct(s):
    """
    datetime -> time_struct

    :param s:
    :return:

    .. code-block:: python

        >>> dt = datetime.datetime.now()
        >>> print dt_to_struct(dt)
    """
    return s.timetuple()


def dt_to_int(s):
    """

    s -> int

    :param s:
    :return:
    """
    timestamp = int(sys_time.mktime(s.timetuple()))
    return timestamp


def struct_to_int(s):
    timeStamp = int(sys_time.mktime(s))
    return timeStamp


def int_to_struct(ts):
    t_info = sys_time.localtime(ts)
    return t_info


def int_to_str(ts, fmt="%Y-%m-%d"):
    t_info = int_to_struct(ts)
    return sys_time.strftime(fmt, t_info)

def dt_to_str(dt, fmt="%Y-%m-%d"):
    return dt.strftime(fmt)


def str_to_o(s, fmt="%Y-%m-%d"):
    ts = sys_time.mktime(sys_time.strptime(s, fmt))
    return CoTime(ts)


def utc():
    """

    :return:
    """
    print(datetime.datetime.utcnow())