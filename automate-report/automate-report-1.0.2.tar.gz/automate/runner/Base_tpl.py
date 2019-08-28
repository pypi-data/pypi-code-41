# coding=utf-8

# 倒入所有HTML 模块
from .Template import *

# 测试报告HTML 模板类, 跳过不用看
# ----------------------------------------------------------------------
# Template
# ----------------------------------------------------------------------
class Base_tpl(object):
    """
    Define a HTML template for report customerization and generation.
    定义一个模板类

    Overall structure of an HTML report   # HTML报告的总体结构

    HTML
    +------------------------+
    |<html>                  |
    |  <head>                |
    |                        |
    |   STYLESHEET           |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |  </head>               |
    |                        |
    |  <body>                |
    |                        |
    |   HEADING              |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |   REPORT               |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |   ENDING               |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |  </body>               |
    |</html>                 |
    +------------------------+
    """

    STATUS = {
        0: '<span style=\'color:#6c6;font-weight:bold\'>通过</span>',
        1: '<span style=\'color:#d60000\'>失败</span>',
        2: '<span style=\'color:#e74c3c\'>错误</span>',
    }
    #  测试用例运行的结果

    DEFAULT_TITLE = 'Unit Test Report'   #默认的标题
    DEFAULT_DESCRIPTION = ''  #默认的描述



