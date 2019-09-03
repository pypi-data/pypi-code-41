# coding=utf-8
from __future__ import print_function

import os
import sys
import re

import time
import json
import platform
import requests

from .utils import hitc


class Model(object):
    def __init__(self):
        super(Model, self).__init__()

    # 创建模型目录和添加初始版本
    def save_one(self, name, task_type, json_path, param_path, dept, level, framework=None, usage=None):
        """
            Return success or fail or error.

            Parameters
            ----------
            name      : set gpu model name
            task_type : set gpu model's tasktype, currently support detection|classification|
                        segmentation|landmarks|skeleton|face recognition|person re-identification|
                        multi-object tracking|face anti-spoofing|traffic lane|multitask|head_pose
            
            json_path : set gpu model json file (default "model.json")
                        ***hdfs://hobot-bigdata/user/jing01.wang/model/model_v2.10.2.json

            param_path: set gpu model param file (default "model.param")
                        ***hdfs://hobot-bigdata/user/jing01.wang/model/model_v2.10.2.params

            dept      : set department for gpu model

            level     : set gpu model permission,currently support private|
                        public,optional (default "private")

            framework : set gpu model's framework, currently support MXNet|
                        TensorFlow|PyTorch (default "MXNet")

            usage     : set gpu model's usage, currently support for inference|
                        for compile|others (default "for inference")


            Examples
            --------
            from olympus import model

            model = model.Model()

            name = "first_modelv1.84"
            task_type = "detection"
            json_path = "C:\\Users\\v-yu.gao\\goworkpath\\olympus\\app\\cmd\\model_v2.10.2.json"
            param_path = "C:\\Users\\v-yu.gao\\goworkpath\\olympus\\app\\cmd\\model_v2.10.2.params"
            ***
                支持传文件在hdfs的路径
                json_path = "hdfs://hobot-bigdata/user/jing01.wang/model/model_v2.10.2.json"
                param_path = "hdfs://hobot-bigdata/user/jing01.wang/model/model_v2.10.2.params"
            ***
            dept = "aiot"
            level = "public"
            framework = "MXNet"
            usage = "for inference"

            print(model.save_one(name, task_type, json_path, param_path, dept, level, framework, usage))    


        """


        if not usage:
            usage = r'"for inference"'

        if not framework:
            framework = "MXNet"


        command = [
            "model", "create", "-n", name, "-t", task_type, "-j", json_path,
            "-p", param_path, "--dept", dept, "--perm", level, "-f",framework,
            "-u",r'"%s"'%(usage)
        ]

        return hitc(command)

    # 给已存在的模型目录添加版本
    def append_one(self, parent_id, json_path, param_path, framework=None, usage=None):
        """
            Return success or fail or error.

            Parameters
            ----------
            id        : set model dir's id
            json_path : set gpu model json file (default "model.json")
                        ***hdfs://hobot-bigdata/user/jing01.wang/model/model_v2.10.2.json

            param_path: set gpu model param file (default "model.param")
                        ***hdfs://hobot-bigdata/user/jing01.wang/model/model_v2.10.2.params

            framework : set gpu model's framework, currently support MXNet|
                        TensorFlow|PyTorch (default "MXNet")

            usage     : set gpu model's usage, currently support for inference|
                        for compile|others (default "for inference")


            Examples
            --------
            from olympus import model

            model = model.Model()

            pid = 266

            json_path = "C:\\Users\\v-yu.gao\\goworkpath\\olympus\\app\\cmd\\model_v2.10.2.json"
            param_path = "C:\\Users\\v-yu.gao\\goworkpath\\olympus\\app\\cmd\\model_v2.10.2.params"
            ***
                支持传文件在hdfs的路径
                json_path = "hdfs://hobot-bigdata/user/jing01.wang/model/model_v2.10.2.json"
                param_path = "hdfs://hobot-bigdata/user/jing01.wang/model/model_v2.10.2.params"
            ***

            framework = "MXNet"
            usage = "for inference"

            model.append_one(pid, json_path, param_path, framework, usage)
        """

        if not usage:
            usage=r'"for inference"'

        if not framework:
            framework = "MXNet"


        command = [
            "model", "append", "--id",
            str(parent_id), "-j", json_path, "-p", param_path,
            "-f", framework, "-u", r'"%s"'%(usage)
        ]
        return hitc(command)

    # 创建模型目录添加初始版本，并通过append命令添加后续的版本
    def save(self, name, task_type, json_paths, param_paths, dept, level, framework=None, usage=None):
        """
            Return success or fail or error.

            Parameters
            ----------
            name       : set gpu model name
            task_type  : set gpu model's tasktype, currently support detection|classification|
                         segmentation|landmarks|skeleton|face recognition|person re-identification|
                         multi-object tracking|face anti-spoofing|traffic lane|multitask|head_pose
            
            json_paths : set a list of gpu model json files
            param_paths: set a list of gpu model param files
                         ***hdfs://hobot-bigdata/user/jing01.wang/model/model_v2.10.2.params

            dept       : set department for gpu model
            level      : set gpu model permission,currently support private|
                         public,optional (default "private")

            framework  : set gpu model's framework, currently support MXNet|
                         TensorFlow|PyTorch (default "MXNet")

            usage      : set gpu model's usage, currently support for inference|
                         for compile|others (default "for inference")

                

            Examples
            --------
            from olympus import model
            
            model = model.Model()

            name = "first_modelv1.85"
            task_type = "detection"

            json_path = "C:\\Users\\v-yu.gao\\goworkpath\\olympus\\app\\cmd\\model_v2.10.2.json"
            param_path = "C:\\Users\\v-yu.gao\\goworkpath\\olympus\\app\\cmd\\model_v2.10.2.params"
            ***
                支持传文件在hdfs的路径
                json_path = "hdfs://hobot-bigdata/user/jing01.wang/model/model_v2.10.2.json"
                param_path = "hdfs://hobot-bigdata/user/jing01.wang/model/model_v2.10.2.params"
            ***

            dept = "aiot"
            level = "public"
            framework = "MXNet"
            usage = "for inference"

            json_paths = []
            param_paths = []

            for x in range(3):
                json_paths.append(json_path)
                param_paths.append(param_path)

            model.save(name, task_type, json_paths, param_paths, dept, level, framework, usage)


        """
        result = []
        begin = 0
        parent_id = None

        res = self.save_one(name, task_type, json_paths[0], param_paths[0],
                            dept, level, framework, usage)

        if res.startswith("success") and re.search(r'\d+', res):
            # success, created gpu model dir's id is 237"
            parent_id = re.search(r'\d+', res).group()

            begin = 1
            result.append('succeed : {} {} {} {} {} {}'.format(
                name, task_type, json_paths[0], param_paths[0], dept, level))

        # model create failed, error: GPU model name already exist.
        elif re.search("name already exist", res):
            begin = 0


        for json_path, param_path in zip(json_paths[begin:],
                                         param_paths[begin:]):
            if parent_id:

                res = self.append_one(parent_id, json_path, param_path, framework, usage)

                if not res.startswith("success"):
                    result.append('failed : {} {} {} {} {} {}'.format(
                        name, task_type, json_path, param_path, dept, level))

                else:
                    result.append('succeed : {} {} {} {} {} {}'.format(
                        name, task_type, json_path, param_path, dept, level))

        return result

    # 模型下载
    def download(self, idx):
        """
            Return success or fail or error.

            Parameters
            ----------
            idx     : set model's id
           

            Examples
            --------
            from olympus import model

            model = model.Model()

            idx = 224
            model.download(224) 


        """
        command = ["model", "download", "--id", str(idx)]

        res = hitc(command)
        if res.startswith("model get failed"):
            print (res)
            return None

        elif res.startswith(
                "panic: interface conversion: interface {} is nil"):
            print (res)
            return None

        else:
            print("download model id %s " % str(idx))
            return True

    # 算法模型单条删除
    def delete(self, idx):
        # Are you sure to delete gpu model dir:  first_modelv1.6
        # y/n?
        # yes
        # success
        if not isinstance(idx, int):
            print("id :%s is error" % idx)
            return

        res = hitc(["model", "delete", "--help"])  # .stdout.read()
        # res = hitcx(["model", "delete", "-k", str(idx)])#.stdout.read()
        # print (dir(res))
        # print (res.stdout.read())
        # p.stdin.flush()
        print(res)
        # if res.startswith("Are you sure to delete gpu model"):
        #     print ("????????")
        #     # return hitc(["yes"])
        # else:
        return res
