# -*- coding: utf-8 -*-
# @Time    : 2019/8/12 0012 23:34
# @Author  : Vincent
# @Email   : Vincent@163.com
# @File    : numpv.py
# @Software: PyCharm
from faker import Faker
from faker.providers import BaseProvider
import random

fake = Faker()

class NumProvider(BaseProvider):
    def num(self):
        ri = self.randomInt()
        return str(ri())

    def randomInt(self):
        return lambda a=1,b=30:random.randint(a,b)