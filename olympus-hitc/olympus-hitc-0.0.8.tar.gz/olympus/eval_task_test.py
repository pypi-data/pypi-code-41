# -*- coding: UTF-8 -*-
import unittest


class TaskTest(unittest.TestCase):  # 继承unittest.TestCase
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
        import eval_task

        self.task = eval_task.Task()
        self.configFile_path = "task_config.yaml"

        
    def test_start(self):
        self.task.start(self.configFile_path)

if __name__ == '__main__':
    unittest.main()#运行所有的测试用例

    