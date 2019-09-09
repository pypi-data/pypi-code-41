# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 10:14:03 2019

@author: 10167232
"""

import __main__ as _main_module
import h5py




from .__Config import type_level
from .__Config import path
from .__method import add_path
from .__method import get_path
type_list = type_level[0]

def to_HDF5(name = '',path = path):
    if name == '':
        path = add_path(path,'h5')
        if path == -1:
            return -1
    else:
        path = name
    try:
        HDF = h5py.File(path,mode = 'a')
        for i in _main_module.__dict__.copy().items():
            if str(type(i[1])).split("'")[1] in type_list and i[0][0] != '_':
                HDF.create_dataset(i[0],data= i[1])
                #print(i[0])
        HDF.close()
        print(path)
    except:
        print("io出错")
def from_HDF5(name = '',replace = False,path = path):
    if name == '':
        path = get_path(path,'h5')
        if path == -1:
            return -1
    else:
        path = name
    try:
        HDF = h5py.File(path,mode = 'r')
        for i in HDF.keys():
            if hasattr(_main_module,i) and replace == False or str(type(HDF[i][()])).split("'")[1] not in type_list:
                pass
            else:
                print(i[0])
                setattr(_main_module,i,HDF[i][()])
        HDF.close()
    except:
        print('io出错')