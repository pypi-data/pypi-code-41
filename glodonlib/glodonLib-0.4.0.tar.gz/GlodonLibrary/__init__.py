# -- coding: utf-8 --

from GlodonLibrary.keywords import *
from .version import VERSION


class GlodonLibrary(
    PublicFunction,
    Control,
    HttpReq,
    FileRead,
    BaseFunc,
    RedisFunc,
    SysCon
):

    """自定义的方法库"""
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = VERSION
