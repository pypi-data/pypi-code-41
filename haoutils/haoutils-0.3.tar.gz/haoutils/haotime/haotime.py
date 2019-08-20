# -*- encoding: utf-8 -*-
'''
@File    :   haotime.py
@Time    :   2019/08/05 11:18:42
@Author  :   hao qihan 
@Version :   0.1
@Contact :   2263310007@qq.com
'''
import time


def standard_time_to_time(strtime: str) -> float:
    """ 
    标准时间字符串转为时间戳
    :strtime 固定格式的字符串  Mon May  6 15:43:48 2019
    :return :返回 一个时间戳
    """
    timeint = time.strptime(strtime, "%a %b %d %H:%M:%S %Y")
    return time.mktime(timeint)


def ordinary_time_to_time(strtime: str) -> float:
    """
    yyyy-MM-dd格式的字符串转换为时间戳
    :strtime 固定格式的字符串 2019-08-05 11:18:42
    :return :返回 一个时间戳
    """
    timeint = time.strptime(strtime, "%Y-%m-%d %H:%M:%S")
    return time.mktime(timeint)


def time_to_ordinary_time(inttime: float) -> str:
    """
    时间戳转字符串 
    :floattime 时间戳 1564975122
    :return 时间字符串 2019-08-05 11:18:42
    """
    timeArray = time.localtime(inttime)
    strtime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return strtime


def time_to_standard_time(inttime: float) -> str:
    """
    时间戳转字符串 
    :floattime 时间戳 1564975122
    :return 时间字符串 
    """
    timeArray = time.localtime(inttime)
    strtime = time.strftime("%a %b %d %H:%M:%S %Y", timeArray)
    return strtime


if __name__ == "__main__":
    time_to_standard_time(1564975122.0)
