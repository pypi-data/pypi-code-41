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
        if not usage:
            usage = r'"for inference"'

        if not framework:
            framework = "MXNet"


        command = [
            "model", "create", "-n", name, "-t", task_type, "-j", json_path,
            "-p", param_path, "--dept", dept, "--perm", level, "-f",framework,
            "-u",r'"%s"'%(usage)
        ]
        # success, created gpu model dir's id is 237
        return hitc(command)

    # 给已存在的模型目录添加版本
    def append_one(self, parent_id, json_path, param_path, framework=None, usage=None):
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
        # model download --id
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
