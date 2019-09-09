"""
建议使用HDF5格式
to_HDF5:变量保存为HDF5格式
from_HDF:从HDF5格式读取变量
dumps:保存内存中的变量
loads:读取已保存的变量到主命名空间（顺便引入numpy、pandas）
var_view:查看命名空间中的变量
clear_var:清除变量


Created on Thu Sep  5 14:11:55 2019

@author: karond
"""

__version__ = "0.3.1"
__author__ = 'karond'


from .__vars_pickle import dumps
from .__vars_pickle import loads
from .__vars_manga import var_view
from .__vars_manga import clear_var
from .__HDF5 import to_HDF5
from .__HDF5 import from_HDF5