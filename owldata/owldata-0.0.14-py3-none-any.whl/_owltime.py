#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# =====================================================================
# Copyright (C) 2018-2019 by Owl Data
# author: Danny, Destiny

# =====================================================================

import datetime
from ._owlerror import OwlError

def _count_dates(begin, end, trans = 'm'):
    '''
    輸入起訖日期，依據字元數區分年季日格式，計算出區間長度
    parameters
    ------------
    :parame begin: str
        輸入八碼 查詢日資料的區間長度；輸入六碼 查詢季或月資料的區間長度；輸入四碼 查詢年資料的區間長度
    
    :parame end: str
        輸入八碼 查詢日資料的區間長度；輸入六碼 查詢季或月資料的區間長度；輸入四碼 查詢年資料的區間長度
    :parame trans: str
        - 輸入季別與月份轉換, m = 月份 ; s = 季別
    Returns
    ---------
    :str: 輸出一個期數
    
    Examples
    ---------
    日資料: count_dates("20180101","20180131")
        Out: 31
    季資料: count_dates("201702","201901")
        Out: 8
    年資料: count_dates("2017","2019")
        Out: 3
    
    [Notes]
    -------
    計算期數時，+1是為了加上期初的第一筆
    起始日<結束日: 會出現錯誤訊息，並以 _dicts 回傳文字訊息
    日資料的日期大於該月最後一日: 會出錯誤訊息，並以 _dicts 回傳文字訊息
    '''
    # 轉換日期長度
    if len(begin)==8 and len(end)==8:
        diff=datetime.datetime.strptime(end, "%Y%m%d") - datetime.datetime.strptime(begin, "%Y%m%d")
        if (diff.days>=0):
            return str(diff.days+1)
        else:
            print(OwlError._dicts["DateError"])
            return "err"
    # 轉換月期長度
        
    elif (len(begin)==6 and len(end)==6 and trans == 'm'):
        year_begin=datetime.datetime.strptime(begin,"%Y%m").year
        month_begin=datetime.datetime.strptime(begin,"%Y%m").month
        year_end=datetime.datetime.strptime(end,"%Y%m").year
        month_end=datetime.datetime.strptime(end,"%Y%m").month
        diff=(year_end-year_begin)*12+(month_end-month_begin)
        if (diff>=0):
            return str(diff+1)
        else:
            print(OwlError._dicts["DateError"])
            return "err"    

        
    # 轉換季度長度
    elif (len(begin)==6 and len(end)==6) and int(begin[4:6])<=4 and int(end[4:6])<=4 and trans == 's':
        year_begin=datetime.datetime.strptime(begin,"%Y%m").year
        month_begin=datetime.datetime.strptime(begin,"%Y%m").month
        year_end=datetime.datetime.strptime(end,"%Y%m").year
        month_end=datetime.datetime.strptime(end,"%Y%m").month
        diff=(year_end-year_begin)*4+(month_end-month_begin)
        if (diff>=0):
            return str(diff+1)
        else:
            print(OwlError._dicts["DateError"])
            return "err"
        
    # 轉換年度的長度
    elif len(begin)==4 and len(end)==4:
        diff=int(end)-int(begin)
        if (diff>=0):
            return str(diff+1)
        else:
            print(OwlError._dicts["DateError"])
            return "err"