#!/usr/bin/python
# -*- coding: UTF-8 -*-
# coding:utf-8
import os, time, unittest
from txInterface import htmlTestReportCN, basic
from txInterface.log import logger


def runcase(params):
    logger.info(params)
    list=[]
    currentDir = os.path.abspath(os.path.dirname(__file__))
    proDir = os.path.split(currentDir)[0]
    logger.info(currentDir)
    logger.info(proDir)
    for param in params:
        shijian  = basic.getcurrenttime("").replace(" ", "")
        discover = unittest.defaultTestLoader.discover(currentDir, pattern=param + "*.py", top_level_dir=None)
        filename = os.path.join("report", param + shijian + ".html")
        fp = open(filename, "wb")
        runner = htmlTestReportCN.HTMLTestRunner(stream=fp,
                                                 tester='刘冬雪',
                                                 title=u'推想接口自动化测试报告：',
                                                 description=u'用例执行情况：')
        runner.run(discover)
        list.append(filename)
        time.sleep(5)
        fp.close()
    return list
if __name__ == '__main__':
        runcase(['test'])