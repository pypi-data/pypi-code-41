# -*- coding: utf-8 -*-
# @Time    : 2019/8/7 14:40
# @Author  : Vincent
# @Email   : Vincent@163.com
# @File    : RedisUtil.py
# @Software: PyCharm

import redis
import ast

class RedisUtil:
    def __init__(self, host='localhost', port=6379, db=0):
        self.host = host
        self.port = port
        self.db = db
        self.__initredis()


    def __initredis(self):
        self.redis = redis.Redis(self.host, self.port, self.db)


    def getdata(self,key):
        return self.redis.get(key)


# r=RedisUtil("172.20.0.54")
# c=r.getdata("lion:conteactCenter:conteactCenter_mysql_account")
# s=str(c,'utf-8')
# d=ast.literal_eval(s)
# print(d["userName"])