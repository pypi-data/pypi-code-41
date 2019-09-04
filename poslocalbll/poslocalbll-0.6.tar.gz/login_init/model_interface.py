# coding=utf-8
'''
author:hexiaoxia
date:2019/09/03
与model层通信接口
'''
from poslocalmodel.pos_sys.pos_global_obj import PosGlobalObj
class ModelInterface(object):

    def __init__(self):
        pass

    def getparam_checkcpu(self):
        cpu=PosGlobalObj.Cpuserialnumber
        return {"CPU":cpu}

class_dict = {key: var for key, var in locals().items() if isinstance(var, type)}