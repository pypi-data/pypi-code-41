# -*- coding: utf-8 -*-
"""
继承自定义库中的类，rfw会解析类中的函数作为关键词
"""
from .PublicLibrary import PublicLibrary
from .RobotExtend import RobotExtend
from .version import VERSION


__author__ = 'Bryan Hou'
__email__ = 'bryanhou@gmail.com'
__version__ = VERSION

class PublicLibrary(PublicLibrary):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_DOC_FORMAT = "ROBOT"