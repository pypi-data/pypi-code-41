# -*- coding: utf-8 -*-
# @Time    : 2019/8/12 0012 23:20
# @Author  : Vincent
# @Email   : Vincent@163.com
# @File    : user.py
# @Software: PyCharm

import factory
class User():
    def __init__(self, name, num, age, school, city, phone):
        self.name, self.num, self.age, self.school, self.city, self.phone = \
            name, num, age, school, city, phone
