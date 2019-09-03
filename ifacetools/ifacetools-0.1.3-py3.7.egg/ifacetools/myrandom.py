# -*- coding: utf-8 -*-
# @Time    : 2019/8/4 0004 10:05
# @Author  : Vincent
# @Email   : Vincent@163.com
# @File    : MyRandom.py
# @Software: PyCharm

import random
import uuid


def randomStr(num=1):
    ri=randomInt()
    s=''
    for i in range(num):
        s=s+str(ri())
    return s

def randomInt():
    return lambda a=0,b=9:random.randint(a,b)

def uuidWithHyphen():
    return str(uuid.uuid4())

def uuidAfterReplace():
    s=uuidWithHyphen()
    return s.replace("-","")


#print(type(randomStr()))
#print(uuidWithHyphen())
#print(uuidAfterReplace())