#!usr/bin/env python
# coding=utf-8

from robot.api import TestSuite
from .version import VERSION

__author__ = 'bryan hou'
__email__ = 'bryanhou@gmail.com'
__version__ = VERSION

class RobotExtend(object):
    """
    调用RobotFramework的方法
    eg：
    re = RobotExtend.RobotExtend()
    re.exec_keywords('xxx.robot', ['获取随机数', '获取计数'])
    """

    def exec_keyword(self, path_to_file, keyword, arg=None):
        """
        执行RobotFramework的关键字
        :param path_to_file: String，RobotFramework文件的路径，一般是执行文件的相对路径，绝对路径也可以
        :param keyword: String，执行的关键字
        :param arg: List[String], 执行关键字的参数，如果没有则不传
        :return: None， 没有返回则表示执行通过，可以查看执行文件目录下的log.html来定位问题
        """
        suite = TestSuite('Test')
        suite.resource.imports.resource(path_to_file)
        test = suite.tests.create('TEST', tags=['smoke'])
        if arg:
            if isinstance(arg, list):
                test.keywords.create(keyword.decode('utf-8'), args=arg)
            else:
                raise TypeError('args must be list')
        else:
            test.keywords.create(keyword.decode('utf-8'))
        result = suite.run(critical='smoke')
        if result.suite.status == 'PASS':
            pass
        else:
            ResultWriter('test.xml').write_results()
    if '__name__' == '__main__':
        exec_keyword(self,path_to_file, keyword, arg=None)
