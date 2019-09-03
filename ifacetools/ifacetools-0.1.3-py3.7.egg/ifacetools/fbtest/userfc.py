# -*- coding: utf-8 -*-
# @Time    : 2019/8/12 0012 23:26
# @Author  : Vincent
# @Email   : Vincent@163.com
# @File    : userfc.py
# @Software: PyCharm
import factory
import factory.fuzzy
from fbtest.user import User
from fbtest.school import School
from fbtest.numpv import NumProvider

factory.Faker.add_provider(NumProvider)

class SchoolFactory(factory.Factory):
    class Meta:
        model = School

    schoolName=factory.sequence(lambda n: 'school%04d' % n)



class UserFactory(factory.Factory):
    class Meta:
        model = User

    name=factory.Faker("name",locale="zh_CN")
    num=factory.Faker("num")
    age=factory.fuzzy.FuzzyInteger(42)
    city=factory.Faker("address",locale="zh_CN")
    phone=factory.fuzzy.FuzzyText("138",7,"1","1234567890")
    school=factory.SubFactory(SchoolFactory)

    class Params:
        shipped=factory.Trait(
            name=None
        )