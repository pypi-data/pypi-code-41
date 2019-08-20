# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on MAY 21, 2018
@author: zhanglanhui
homepage recommender:ffm
"""
import datetime
import time


def get_before_date(days=1):
    today = datetime.date.today()
    oneday = datetime.timedelta(days=days)
    yesterday = today - oneday
    return yesterday


def get_after_date(days=1):
    today = datetime.date.today()
    oneday = datetime.timedelta(days=days)
    yesterday = today + oneday
    return yesterday


def getYesterday():
    yesterday = datetime.date.today() + datetime.timedelta(-1)
    return yesterday


def today_time_d():
    return time.strftime("%Y-%m-%d", time.localtime())


def today_time_s():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def get_date_from_timstamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)


def get_date_from_str(dtstr):
    return datetime.datetime.strptime(dtstr, "%Y-%m-%d")


if __name__ == "__main__":
    print(get_after_date(1))
    print(get_before_date(1))
    print(today_time_s())
