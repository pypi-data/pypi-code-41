# -*- coding: utf-8 -*-
"""
dumps:保存内存中的变量
loads:读取已保存的变量到主命名空间（顺便引入numpy、pandas）
type_list:需要保存的变量类型
drop_list:不想保存的变量列表（主要针对jupyter）


Created on Thu Sep  5 14:11:55 2019

@author: karond
"""
import __main__ as _main_module
import pickle
import datetime
import os
import numpy as np
import pandas as pd
import config

type_list = config.type_list
drop_list = config.drop_list
path = config.path


def dumps(name = '',path = path):
    """
    默认保存到：./data_pickle/%Y-%m-%d/%H-%M-%S.pkl
    name:自定义变量保存位置
    path:保存数据的文件夹位置
    """
    if name == '':
        path = os.path.join(path,datetime.datetime.now().strftime('%Y-%m-%d'))
        if not os.path.exists(path):
            os.makedirs(path)
            print('创建'+path)
        path = os.path.join(path,datetime.datetime.now().strftime('%H-%M-%S'))+'.pkl'
    else:
        path = name
    pickl = []
    for i in _main_module.__dict__.copy().items():
        if i[0][0] != '_' and str(type(i[1])).split("'")[1] in type_list and i[0] not in drop_list:
            pickl.append(i)
    try:
        pickl = tuple( pickl )
        f = open(path,'wb')
        pickle.dump(pickl,f)
        f.close()
        print("pickle:"+path)
    except:
          print('pickle ERROR')
def loads(name = '',replace = False,path = path):
    """
    默认读取：./data_pickle/%Y-%m-%d/%H-%M-%S.pkl中最新的文件
    name:自定义变量读取位置
    replace:是否替换已经定义的变量
    path:读取数据的文件夹位置
    """
    try:
        if name == '':
            dir_list = [datetime.datetime.strptime(i,'%Y-%m-%d') for i in os.listdir(path)]
            path = os.path.join(path,max(dir_list).strftime('%Y-%m-%d'))
            dir_list = [datetime.datetime.strptime(i.split('.')[0],'%H-%M-%S') for i in os.listdir(path)]
            path = os.path.join(path,max(dir_list).strftime('%H-%M-%S'))+'.pkl'
        else:
            path = name
        setattr(_main_module,'np',np)
        setattr(_main_module,'pd',pd)
        f = open(path,'rb')
        pickl = pickle.load(f)
        for i in pickl:
            if hasattr(_main_module,i[0]) and replace == False:
                pass
            else:
                print(i[0])
                setattr(_main_module,i[0],i[1])
        print('laod:'+path)
    except:
        print('load ERROR')
