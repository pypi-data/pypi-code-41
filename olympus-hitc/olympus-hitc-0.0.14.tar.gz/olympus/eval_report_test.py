# -*- coding: UTF-8 -*-
import unittest
from . import eval_report


class ReportTest(unittest.TestCase):  # 继承unittest.TestCase
    def tearDown(self):
        # 每个测试用例执行之后做操作
        print('22222222-----------over--------------')

    def setUp(self):
        # 每个测试用例执行之前做操作
        print('11111111-----------begin-------------')

    @classmethod
    def tearDownClass(self):
        # 必须使用 @ classmethod装饰器, 所有test运行完后运行一次
        pass

    @classmethod
    def setUpClass(self):
        # 必须使用@classmethod 装饰器,所有test运行前运行一次
        self.report = eval_report.Report()
        self.configFile_path = "eval_report.json"

        
    def test_create(self):
        self.report.create(self.configFile_path)
   

if __name__ == '__main__':
    unittest.main()#运行所有的测试用例
    