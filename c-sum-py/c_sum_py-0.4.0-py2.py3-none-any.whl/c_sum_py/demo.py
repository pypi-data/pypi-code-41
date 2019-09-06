"""
一个python调用dll库的简单demo
参考文章: https://python3-cookbook.readthedocs.io/zh_CN/latest/c15/p01_access_ccode_using_ctypes.html
"""
"""
# 下面是一个可行的方式(模仿链接)
import ctypes
import os

_dll_file = 'c_sum.dll'
_path = os.path.join(*(os.path.split(__file__)[:-1] + (_dll_file,)))
print(_path)  # 测试路径
print(__file__)  # 测试__file__的值, 是这个py文件的目录

_mod = ctypes.cdll.LoadLibrary(_path)  # 中间也可以用windll

print(_mod.sum(1, 2))
"""

# 一个调用c语言的最小代码
import ctypes
import os
from c_sum_py import c_sum

_dll_file = 'c_sum.dll'
_path = os.path.join(*(os.path.split(__file__)[:-1] + (_dll_file,)))
fromc = ctypes.cdll.LoadLibrary(_path)  # 似乎是需要给出完整的目录

print(fromc.sum(1, 3))
print(type(fromc.sum(1, 3)))

print(c_sum.sum(4, 5))