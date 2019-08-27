# -*- coding: UTF-8 -*-
import unittest


class MyTest(unittest.TestCase):  # 继承unittest.TestCase
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
        import model
        self.model = model.Model()


    # def test_save_one(self):
    #     #.\hitc.exe model create -n first_modelv1.0 -t detection -j .\model_v2.10.2.json -p .\model_v2.10.2.params --dept aiot --perm private
    #     # name = "first_modelv1.%s"%(random.randint(1,3))
    #     name = "first_modelv1.94"
    #     task_type = "detection"
    #     # task_type = ""
    #     json_path = "C:\\Users\\v-yu.gao\\goworkpath\\olympus\\app\\cmd\\model_v2.10.2.json"
    #     param_path = "C:\\Users\\v-yu.gao\\goworkpath\\olympus\\app\\cmd\\model_v2.10.2.params"
    #     dept = "aiot"
    #     level = "public"

    #     print(self.model.save_one(name, task_type, json_path, param_path, dept, level))    

    # def test_save_one_append(self):
    #     #.\hitc.exe model create -n first_modelv1.0 -t detection -j .\model_v2.10.2.json -p .\model_v2.10.2.params --dept aiot --perm private
    #     # name = "first_modelv1.%s"%(random.randint(1,3))
    #     name = "first_modelv1.94"
    #     task_type = "detection"
    #     # task_type = ""
    #     json_path = "C:\\Users\\v-yu.gao\\goworkpath\\olympus\\app\\cmd\\model_v2.10.2.json"
    #     param_path = "C:\\Users\\v-yu.gao\\goworkpath\\olympus\\app\\cmd\\model_v2.10.2.params"
    #     dept = "aiot"
    #     level = "public"

    #     print(self.model.save_one_append(name, task_type, json_path, param_path, dept, level))    

    # def test_save(self):
    #     name = "first_modelv1.95"
    #     task_type = "detection"
    #     # task_type = ""
    #     json_path = "C:\\Users\\v-yu.gao\\goworkpath\\olympus\\app\\cmd\\model_v2.10.2.json"
    #     param_path = "C:\\Users\\v-yu.gao\\goworkpath\\olympus\\app\\cmd\\model_v2.10.2.params"
    #     dept = "aiot"
    #     level = "public"


    #     json_paths = []
    #     param_paths = []

    #     for x in range(3):
    #         json_paths.append(json_path)
    #         param_paths.append(param_path)

    #     print(self.model.save(name, task_type, json_paths, param_paths, dept, level))


    def test_download(self):
        idx = 224
        print(self.model.download(224))

if __name__ == '__main__':
    unittest.main()#运行所有的测试用例
