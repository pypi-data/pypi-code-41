# -*- coding: utf-8 -*-
# @Time    : 2019/8/4 0004 17:04
# @Author  : Vincent
# @Email   : Vincent@163.com
# @File    : JSONUtil.py
# @Software: PyCharm

import json

class JSONUtil:

    def josnStingToDict(self,str="{}"):
        return json.loads(str)

    def pythonObjectToJosnSting(self,p):
        try:
           j= json.dumps(dict(p),ensure_ascii=False)
        except TypeError:
            raise TypeError("该对象没有实现 keys和 __getitem__")
        else:
            print(j)
        return j

    def dictToJosnSting(self,dict={"a":1}):
        try:
           j= json.dumps(p,ensure_ascii=False)
        except TypeError:
            raise TypeError("仅支持字典转换成json串")
        else:
            print(j)
        return j

    def dictToJosnStingWithSort(self,dict={"a":1}):
        try:
           j= json.dumps(p,sort_keys=True,ensure_ascii=False)
        except TypeError:
            raise TypeError("仅支持字典转换成json串")
        else:
            print(j)
        return j

# j=JSONUtil()
#
# p='{"f":"f1","a":"a","b":[{"c":1},{"c":2}]}'
# #p = '{"a":"a","b":2}'
# p =  j.josnStingToDict(p)
# print(p)
# print(p.get('a'))
# print(p.get('b')[0])
# print(p.get('b')[1].get("c"))
#
# dicts={"f":"f1","a":"a","b":[{"c":1},{"c":2}]}
# print(j.dictToJosnSting(dicts))
# print(j.dictToJosnStingWithSort(dicts))
#
#
#
# class User:
#     name = 'wukt'
#     age = 18
#
#     def __init__(self):
#         self.gender = 'male'
#
#
#     def keys(self):
#         '''当对实例化对象使用dict(obj)的时候, 会调用这个方法,这里定义了字典的键, 其对应的值将以obj['name']的形式取,
#         但是对象是不可以以这种方式取值的, 为了支持这种取值, 可以为类增加一个方法'''
#         return ('name', 'age', 'gender')
#
#     def __getitem__(self, item):
#         '''内置方法, 当使用obj['name']的形式的时候, 将调用这个方法, 这里返回的结果就是值'''
#         return getattr(self, item)
#
# u=User()
# #print(dict(u))
# print(j.pythonObjectToJosnSting(u))

