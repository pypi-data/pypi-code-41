# -*- coding: utf-8 -*-
# @Time    : 2019/8/12 0012 23:40
# @Author  : Vincent
# @Email   : Vincent@163.com
# @File    : use.py
# @Software: PyCharm
from django.forms.models import model_to_dict
import factory
from fbtest.userfc import UserFactory
from fbtest.school import School

seq=[]
uf=UserFactory()
print(uf.__dict__)
seq.append(uf.__dict__)
seq.append(UserFactory().__dict__)
print(seq)


list=[]
fss=factory.build_batch(UserFactory,4)
for fs in fss:
    list.append(fs.__dict__)
print(list)

uff=UserFactory(shipped=True)
print(uff.__dict__)


# uffs=UserFactory(city="1245")
# print(model_to_dict(UserFactory(city="1245")))

