"""
dumps:保存内存中的变量
loads:读取已保存的变量到主命名空间（顺便引入numpy、pandas）
type_list:需要保存的变量类型
drop_list:不想保存的变量列表（主要针对jupyter）


Created on Thu Sep  5 14:11:55 2019

@author: karond
"""

__version__ = "0.1.3"



import vars_pickl as __vars_pickl
import config as __config




drop_list = __config.drop_list
type_list = __config.type_list


dumps = __vars_pickl.dumps
loads = __vars_pickl.loads