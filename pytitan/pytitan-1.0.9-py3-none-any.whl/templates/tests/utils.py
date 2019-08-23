# coding: utf-8

from faker import Faker
from faker.providers import BaseProvider
from faker.providers.internet import ip_address, ip_network

fake = Faker('zh_CN')
fake.add_provider(ip_address)
fake.add_provider(ip_network)

# 要生成自定义数据请启用以下代码并进行相应修改
#
# class CustomFakerProvider(BaseProvider):
#     pass
#
# fake.add_provider(CustomFakerProvider)