# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 10:23:27 2019

@author: 10167232
"""

import datetime
import os

def add_path(path,extension_name):
    try:
        path = os.path.join(path,datetime.datetime.now().strftime('%Y-%m-%d'))
        if not os.path.exists(path):
            os.makedirs(path)
            print('创建'+path)
        path = os.path.join(path,datetime.datetime.now().strftime('%H-%M-%S'))+"."+extension_name
            #print(path)
        return path
    except:
        print('创建失败')
        return -1

def get_path(path,extension_name):
    try:
        dir_list = [datetime.datetime.strptime(i,'%Y-%m-%d') for i in os.listdir(path)]
        path = os.path.join(path,max(dir_list).strftime('%Y-%m-%d'))
        dir_list = [datetime.datetime.strptime(i.split('.')[0],'%H-%M-%S') for i in os.listdir(path)]
        path = os.path.join(path,max(dir_list).strftime('%H-%M-%S'))+'.'+extension_name
        return path
    except:
        print('没有可读文件')
        return -1