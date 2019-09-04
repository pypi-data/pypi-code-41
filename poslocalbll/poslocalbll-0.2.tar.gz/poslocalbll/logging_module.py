# coding=utf-8

import importlib

class Loggingm(object):
    @classmethod
    def debug(self,message):
        method = self.get_funname()  # 方法名
        module = "poswebapp.loggingm.logger"
        module = importlib.import_module(module)  # import module
        fun = None
        module.debug(message)

    @classmethod
    def error(self,message):
        method = self.get_funname()  # 方法名
        module = "poswebapp.loggingm.logger"
        module = importlib.import_module(module)  # import module
        fun = None
        module.error(message)