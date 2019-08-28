# coding=utf-8
import sys
import os
from unittest2 import loader

from automate.common.util import OsUtil
import importlib
from . import MyTestSuite
import datetime
from . import _TestResult as testResult
from automate.runner import Report


# from runner.report import Report   # 导入生成报告的类


class TestCaseRun(object):

    # 多打印一个空行
    def my_print(self, message):
        print("")
        print(message)

    # 第一个参数为json配置路径，第二个参数为输出报告，第三个参数为报告标题，可选填
    def __init__(self,cases_dir, report_dir,title=None):
        ##### 核心代码开始运行 ############################

        # sys.path.insert(0,'模块的名称')  在系统路径的第一个位置插入  sys.path是全局搜索路列表list  在第一个位置为了提升速度，只需找一次就能找到项目位置
        sys.path.insert(0, '..')
        # 用例列表
        cases_list = fileListPy(cases_dir)

        # 输出系统的所有路径
        self.my_print(sys.path)

        # 获取项目根目录 UnitTestFrameWorkDemo
        global_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
        self.my_print(global_path)

        # 获取测试用例集的配置文件
        self.my_print('测试用例路径：' + cases_dir)

        # 初始化存放测试用例集的list数据结构

        # 判断报告文件夹是否存在，若不存在则创建, 测试报告目录按照阿拉伯数字递增 1, 2, 3, 4, 5, 6, 7 ,8
        is_exist = os.path.exists(report_dir)
        if is_exist is False:
            report_dir = report_dir + os.sep + "1"
            os.makedirs(report_dir)  # 建立这个report_dir目录

        else:
            dir_list = []
            for data in os.listdir(report_dir):
                file_dir = report_dir + os.sep + data
                if os.path.isdir(file_dir):
                    dir_list.append(data)
            dir_list.sort()  # 排序报告
            print(dir_list)

            lenth = len(dir_list)
            report_dir = report_dir + os.sep + str(lenth + 1)
            os.makedirs(report_dir)

        ############## 运行指定测试用例集 ###############
        # 设置测试用例套件运行目录
        root = cases_dir
        sys.path.append(root)

        # 构建自定义测试用例套件
        test_suites = MyTestSuite.MyTestSuite()

        # 将配置的测试用例python文件添加到测试用例套件 其实就是调用 MyTestSuite的addTest方法
        for ts_name in cases_list:
            # 用例文件完整的路径,注意要删除前缀的测试用例路径
            if ts_name.startswith(cases_dir):
                ts_name = ts_name.replace(cases_dir + '/', '')
            if ts_name.endswith('.py'):
                ts_name = os.path.splitext(ts_name)[0]
            tc_complete = ts_name.replace('/', '.')
            self.my_print(tc_complete)

            if OsUtil.is_linux():
                test_suites.addTest(loader.TestLoader().discover(tc_complete))
            else:
                module = importlib.import_module(tc_complete)
                test_suites.addTest(loader.TestLoader().loadTestsFromModule(module))

        # 打开测试报告文件流
        file_path = report_dir + os.sep + 'report.html'
        stream = open(file_path, 'wb')

        # 测试开始时间
        startTime = datetime.datetime.now()

        # 构建测试用例结果
        result = testResult._TestResult()
        # 运行测试用例套件
        test_suites(result)

        # 测试结束时间
        stopTime = datetime.datetime.now()

        ################## 开始生成测试报告 ##############
        if title == None:
            title = '用例报告'
        myReport = Report.Report(stream, title, startTime, stopTime)
        myReport.generateReport(test_suites, result, cases_dir)


# 获取该目录下的所有py文件，排除__init__.py
def fileListPy(dirname):
    L = []
    for root, dirs, files in os.walk(dirname):
        for file in files:
            if file != '__init__.py' and os.path.splitext(file)[1] == '.py':
                L.append(os.path.join(root, file))
    return L
