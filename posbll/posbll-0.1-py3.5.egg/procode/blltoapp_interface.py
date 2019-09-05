# coding=utf-8
'''
author:hexiaoxia
date:2019/08/21
bll层调用app层的调用js方法模块接口类
'''

import importlib

class BllToAppInterface(object):
    def __init__(self,module,funname):
        self.__module=module
        self.__funname=funname

    #调用的模块名
    def get_module(self):
        return self.__module

    #调用的方法名
    def get_funname(self):
        return self.__funname


    def executefun(self,jsonparam):
        '''
        bll调用前端js
        :param kwargs:
        :return:
        '''
        method = self.get_funname()  # 方法名
        module = "poswebapp.bll_to_app_function." + self.get_module()
        module = importlib.import_module(module)  # import module
        fun=None
        for name in dir(module):
            attr = getattr(module, name)
            if hasattr(attr, "__module__") and attr.__module__ == module.__name__:
                fun=attr
                break

        fun(jsonparam)

    # def loggerfun(self,jsonparam):
    #     method = self.get_funname()  # 方法名
    #     module = "poswebapp.bll_to_app_function." + self.get_module()
    #     module = importlib.import_module(module)  # import module
    #     fun = None
    #     for name in dir(module):
    #         attr = getattr(module, name)
    #         if hasattr(attr, "__module__") and attr.__module__ == module.__name__:
    #             fun = attr
    #             break



    def __str__(self):
        return str(self.__dict__)


