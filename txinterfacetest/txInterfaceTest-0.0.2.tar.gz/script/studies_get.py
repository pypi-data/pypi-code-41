#!/usr/bin/python
# -*- coding: UTF-8 -*-


"""
FileName    : test_login.py
Author      : ken
Date        : 2018-04-21
Describe    : user the paramUnittest, test login
"""
import json
import unittest
import paramunittest
from txInterface import basic, getValue, jsondiff
from txInterface.log import logger
import publicFile

path = publicFile.getPath("series_predict_ct_lung","txt_name")
logger.info("this path is  " +path)
ip = publicFile.getiport("message", "ip")
logger.info( "this  ip is  " +ip )
port = publicFile.getiport("message", "port")
logger.info ("this is port " + port )
loginCase = getValue.get_txt_value(path)
logger.info (loginCase)
@paramunittest.parametrized(*loginCase)
class LoginTest(unittest.TestCase):
    def setParameters(self, interfacename,case_name, param, excepted):
        self.interfacename = interfacename
        self.case_name = case_name
        self.param = param
        self.excepted = excepted
    def setUp(self):
        pass
    def test_login(self):
        print self.case_name
        if "ip地址" == ip :
            pass
        else:
            self._testMethodDoc = self.case_name
            param = self.interfacename.replace("*", self.param)
            implement = basic.basic(ip, port)
            result = implement.get(param, '')
            json2 = json.loads(self.excepted)
            res = jsondiff.diffKeys(result, json2, 2)
            if res.__len__() > 0:
                self.fail(res)
            else:
                pass
    def tearDown(self):
       pass


if __name__ == '__main__':

    unittest.main()