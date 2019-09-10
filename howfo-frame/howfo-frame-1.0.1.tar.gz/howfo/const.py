#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-07-03
# @Author  : Kelly (weiqin.wang_c@chinapnr.com)
# @Desc    : contains app and routes
# @Version : 1.0.0


class Const(object):
    class ConstError(TypeError):
        pass

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, name, value):
        if self.__dict__.has_key(name):
            raise self.ConstError("不能转换常量 %s" % name)
        if not name.isupper():
            raise self.ConstCaseError('常量名 "%s" 没有全大写' % name)
        self.__dict__[name] = value


import sys
sys.modules[__name__]=Const()