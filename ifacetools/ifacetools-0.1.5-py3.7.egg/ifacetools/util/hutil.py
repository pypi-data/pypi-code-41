# -*- coding: utf-8 -*-
# @Time    : 2019/9/3 10:12
# @Author  : Vincent
# @Email   : Vincent@163.com
# @File    : hutil.py
# @Software: PyCharm


class HUtil:

    def objecttodict(self,obj):
        dict_o = obj.__dict__
        for key, value in dict_o.items():
            print(key, type(value))
            if isinstance(value, (str, int)):  # 不处理str,int的情况
                pass
            elif value is None:
                pass
            elif isinstance(value, list):  # 处理list的情况
                valuelist = []
                for l in value:
                    if isinstance(l, (str, int)):
                        valuelist.append(l)
                    else:
                        valuelist.append(self.objecttodict(l))
                dict_o[key] = valuelist
            elif isinstance(value, dict):
                pass  # 不处理dict的情况
            else:  # 处理普通对象
                dict_o[key] = self.objecttodict(value)
        return dict_o


