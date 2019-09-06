"""
dumps:保存内存中的变量
loads:读取已保存的变量到主命名空间（顺便引入numpy、pandas）
type_list:需要保存的变量类型
drop_list:不想保存的变量列表（主要针对jupyter）


Created on Thu Sep  5 14:11:55 2019

@author: karond
"""

__version__ = "0.1.6"
__author__ = 'karond'


from .__vars_pickle import dumps
from .__vars_pickle import loads
from .__config import drop_list
from .__config import type_list