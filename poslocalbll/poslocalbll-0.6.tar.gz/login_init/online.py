# coding=utf-8
'''
与posserviceapi
'''
from posserviceapi.translator import Translator

class OnLineClass(object):
    request = Translator()
    def __init__(self,module):
        self.__module=module

    # 调用的模块名
    def get_module(self):
        return self.__module

    @classmethod
    def checkHealth(self,**kwargs):
        self.request.paramtype = "body"
        self.request.return_v="original"
        res = self.request.sendRequest(**kwargs)
        return res

    def checkcpu(self,**kwargs):
        self.request.paramtype = "query"
        res=self.request.sendRequest(**kwargs)
        return res

    def regiscpu(self,**kwargs):
        self.request.paramtype = "query"
        res = self.request.sendRequest(**kwargs)
        return res




