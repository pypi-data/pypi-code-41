"""
dumps:保存内存中的变量
loads:读取已保存的变量到主命名空间（顺便引入numpy、pandas）
var_view:查看命名空间中的变量
clear_var:清除变量


Created on Thu Sep  5 14:11:55 2019

@author: karond
"""

__version__ = "0.2.9"
__author__ = 'karond'


from .__vars_pickle import dumps
from .__vars_pickle import loads
from .__vars_manga import var_view
from .__vars_manga import clear_var