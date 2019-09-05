# coding=utf-8
'''
与poslocaldal交互
'''
from poslocaldal.translator import Translator
class OffLineClass(object):

    def __init__(self,module):
        self.__module = module

    # 调用的模块名
    def get_module(self):
        return self.__module

    def checkcpu(self,params=None,apiname=None):
        request = Translator("mytest1.db")
        r = request.getDbObject()
        sql = "SELECT *  from tester "
        data=r.querylist(sql)
        r.closedb()
        return {"code":0,"message":"eeeerrr","data":data}

    def checkcpu1(self,**kwargs):
        request = Translator("mytest1.db")
        r = request.getDbObject()
        sql = "SELECT *  from tester "
        data = r.querylist(sql)
        r.closedb()
        return {"code": 0, "message": "eeeerrr", "data": data}