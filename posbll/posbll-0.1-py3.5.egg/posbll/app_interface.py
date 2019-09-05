# coding=utf-8
'''
author:hexiaoxia
date:2019/08/21
app与bll层通信接口类
'''
from poslocalmodel.enums.public_enums import *
from poslocalmodel.pos_sys.posnowinfo import *
# from poslocalbll.logging_module import logger
import importlib

class AppInterface(object):
    __businessnode = None #当前进行的业务节点
    def __init__(self,module,funname,offoronline=OffOrOnLineEnum.offandon):
        self.__module=module
        self.__funname=funname
        self.__isonline=offoronline

    def set_businessnode(self,busnode):
        self.__businessnode=busnode

    #调用的模块名
    def get_module(self):
        return self.__module

    #调用的方法名
    def get_funname(self):
        return self.__funname

    #当前流程节点
    def get_busnode(self):
        return self.__busnode

    #在线离线是否都使用，值："off" 表示只能
    def get_isonline(self):
        return self.__isonline


    def execute_route_fun(self,**kwargs):
        '''
        前端路由调用的具体业务接口方法实现
        :param kwargs:
        :return:
        '''
        print(kwargs)
        if self.__businessnode!=None and self.__businessnode==kwargs.get("busnode",None):
            return None

        if self.get_isonline() == OffOrOnLineEnum.offandon:
            res=self._onlinefun(**kwargs)
            if res.get("code",-1)!=0:
                res=self._offlinefun(**kwargs)
                return res
            else:
                return res
        elif self.get_isonline() == OffOrOnLineEnum.offline:
            res = self._offlinefun(**kwargs)
            return res
        else:
            res = self._onlinefun(**kwargs)
            return res

    def _onlinefun(self,**kwargs):
        res={"code":-1,"message":""}
        if PosNowInfo.Serverapi==0:
            class_name = "OnLineClass"  # 类名
            module_name = "online"  # 最终模块名(也可以是.py文件)
            method = self.get_funname()  # 方法名
            module = "procode." + self.get_module() + "." + module_name
            module = importlib.import_module(module)  # import module

            # print(getattr(module, "class_dict"))
            c = getattr(module, class_name)
            obj = c(self.get_module())
            mtd = getattr(obj, method)
            res = mtd(**kwargs)  # call def
        else:
            res["code"] =-2  #表示在线业务但当前无网络
            res["message"]="网络不通，无法使用在线功能"
        return res

    def _offlinefun(self,**kwargs):
        class_name = "OffLineClass"
        module_name = "offline"
        method = self.get_funname()  # 方法名
        module = "procode." + self.get_module() + "." + module_name
        module = importlib.import_module(module)  # import module
        c = getattr(module, class_name)
        obj = c()
        mtd = getattr(obj, method)
        res = mtd(**kwargs)  # call def
        return res

    def execute_app_fun(self,module_name):
        '''
        非路由的，客户端python自身业务方法需要app层与其它层通信时模块对象获取
        :param module_name:
        :return:
        '''
        class_name=""
        modulepath = "procode."+self.get_module() + "." + module_name
        try:
            module=importlib.import_module(modulepath)
            cc = getattr(module, "class_dict")
            for k, v in (cc).items():
                if (modulepath) in str(cc[k]):
                    class_name=str(k)
                    break
            c = getattr(module, class_name)
            return c
        except Exception as e:
            # logger.error("实例化失败，模块："+modulepath+",类："+class_name)
            return None

    def __str__(self):
        return str(self.__dict__)
