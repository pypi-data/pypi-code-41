# -*- coding: utf-8 -*-
# @Time    : 2019/8/4 0004 12:48
# @Author  : Vincent
# @Email   : Vincent@163.com
# @File    : TimeUtil.py
# @Software: PyCharm

import time,datetime,string
class TimeUtil:
    '''
    一个获取时间的工具类
    该工具类可以指定输出格式、可以指定时间偏移
    '''

    # def __init__(self):
    #     self.ft="%Y-%m-%d %H:%M:%S"

    @property
    def timeStamp(self):
        return time.time()

    @property
    def currentTimeString(self):
        return time.strftime("%Y%m%d%H%M%S",time.localtime(time.time()))


    def currentTime(self,ft="%Y-%m-%d %H:%M:%S"):
        return time.strftime(ft,time.localtime(time.time()))


    def getTargetWeeks(self,weeks=0,ft="%Y-%m-%d %H:%M:%S"):
        nowTime = datetime.datetime.now()
        targetTime=nowTime + datetime.timedelta(weeks=weeks)
        return targetTime.strftime(ft)

    def getTargetDays(self,days=0,ft="%Y-%m-%d %H:%M:%S"):
        nowTime = datetime.datetime.now()
        targetTime=nowTime + datetime.timedelta(days=days)
        return targetTime.strftime(ft)

    def getTargetHours(self,hours=0,ft="%Y-%m-%d %H:%M:%S"):
        nowTime = datetime.datetime.now()
        targetTime=nowTime + datetime.timedelta(hours=hours)
        return targetTime.strftime(ft)

    def getTargetMinutes(self,minutes=0,ft="%Y-%m-%d %H:%M:%S"):
        nowTime = datetime.datetime.now()
        targetTime=nowTime - datetime.timedelta(minutes=minutes)
        return targetTime.strftime(ft)

    def getTargetSeconds(self,seconds=0,ft="%Y-%m-%d %H:%M:%S"):
        nowTime = datetime.datetime.now()
        targetTime=nowTime + datetime.timedelta(seconds=seconds)
        return targetTime.strftime(ft)

# t=TimeUtil()
# print(t.timeStamp)
# print(t.currentTimeString)
# print(t.currentTime())
# print(t.getTargetWeeks(weeks=1))
# print(t.getTargetDays(-1,"%Y-%m-%d"))
# print(t.getTargetDays(days=-1))
# print(t.getTargetHours(hours=9))
# print(t.getTargetMinutes(minutes=20))
# print(t.getTargetSeconds(seconds=35))
