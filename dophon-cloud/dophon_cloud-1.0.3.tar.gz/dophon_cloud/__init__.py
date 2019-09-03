# coding: utf-8
from gevent import monkey

monkey.patch_all()
from dophon_properties import *

get_properties([DOPHON, CLOUD_CLIENT])

from dophon import cloud_client_properties as properties

DOPHON = 'enhance_pkg'

EUREKA = 'eureka_client'

# 初始化服务单元
# import sys
# for k,v in sys.modules.items():
#     if str(k).startswith('dophon'):
#         print(f'{k}---{v}')
client_cell = __import__(f'dophon_cloud.{eval(properties.center_type.upper())}', fromlist=['dophon_cloud'])
# print(client_cell)
__pre__all__ = []
for field in dir(client_cell):
    if field.startswith('__') and field.endswith('__'):
        continue
    globals()[field] = getattr(client_cell, field)
    __pre__all__.append(field)
# print(__pre__all__)
__all__ = __pre__all__
