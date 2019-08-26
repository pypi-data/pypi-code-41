# coding=utf-8
from __future__ import print_function

import os
import sys
import re

import time
import json
import platform
import requests

from utils import hitc


class Model(object):
    def __init__(self):
        super(Model, self).__init__()

    # 算法模型单条创建
    def save_one(self, name, task_type, json_path, param_path, dept, level):
        command = ["model", "create", "-n", name, "-t", task_type, "-j", json_path, "-p", param_path,"--dept", dept, "--perm", level]  
        return hitc(command)

    # 算法模型单条创建_多版本
    def save_one_append(self, name, task_type, json_path, param_path, dept, level):
        command = ["model", "create", "-n", name, "-t", task_type, "-j", json_path, "-p", param_path,"--dept", dept, "--perm", level]  
        return hitc(command)


    # 算法模型多条创建
    def save(self, name, task_type, json_paths, param_paths, dept, level):
        result = []
        begin = 0

        res = self.save_one(
                    name, task_type, json_paths[0], param_paths[0], dept, level
                )

        if res.startswith("success"):
            begin = 1
            result.append('succeed : {} {} {} {} {} {}'.format(name, task_type, json_paths[0], param_paths[0], dept, level))


        #model create failed, error: GPU model name already exist.
        elif re.search("name already exist", res):
            begin = 0

            ####append 命令追加成功 删除以下两行代码
            result.append('failed : {} '.format(res))
            return result


        for json_path, param_path in zip(json_paths[begin:], param_paths[begin:]):

            res = self.save_one_append(
                    name, task_type, json_path, param_path, dept, level
                )
            
            if not res.startswith("success"):
                result.append('failed : {} {} {} {} {} {}'.format(name, task_type, json_path, param_path, dept, level))

            else:
                result.append('succeed : {} {} {} {} {} {}'.format(name, task_type, json_path, param_path, dept, level))
       
        return result

    # 算法模型下载
    def download(self, idx):
        #model download --id
        command = ["model", "download",  "--id", str(idx)] 
        res = hitc(command)
        if res.startswith("model get failed"):
            return res

        elif res.startswith("panic: interface conversion: interface {} is nil"):
            return res

        else:
            print ("download model id %s "%str(idx))
            return  "success"
    
    # 算法模型单条删除
    def delete(self, idx):
        # Are you sure to delete gpu model dir:  first_modelv1.6
        # y/n?
        # yes
        # success
        if not isinstance(idx ,int):
            print ("id :%s is error"%idx)
            return

        res = hitc(["model", "delete", "--help"])#.stdout.read()
        # res = hitcx(["model", "delete", "-k", str(idx)])#.stdout.read()
        # print (dir(res))
        # print (res.stdout.read())
        # p.stdin.flush()
        print (res)
        # if res.startswith("Are you sure to delete gpu model"):
        #     print ("????????")
        #     # return hitc(["yes"])
        # else:
        return res  



# 保存模型
# name: 模型名称
# task_type: 模型所属的算法任务类型
# json_paths: 需要保存的模型JSON名称列表
# param_paths: 需要保持的模型Params名称列表
# dept: 模型所属的部门名称 支持 auto aiot platform
# level: 模型资源的权限级别，支持 private public
# 返回空表明创建成功，返回非空表示创建失败，返回的信息为失败原因
def save_model(name, task_type, json_paths, param_paths, dept, level):
    for json_path, param_path in zip(json_paths, param_paths):
        res = save_one_model(
            name, task_type, json_path, param_path, dept, level
        )
        if res.get("code") != 0:
            return res.get("err_user_msg")
    return ""


def save_one_model(name, task_type, json_path, param_path, dept, level):
    payload = {}
    payload["container_json_path"] = os.path.join(
        host_path, os.path.relpath(json_path, container_path))
    payload["container_param_path"] = os.path.join(
        host_path, os.path.relpath(param_path, container_path))
    payload["name"] = name
    payload["task_type"] = task_type
    payload["auth_info"] = {
        "level": level,
        "deptid": dept
    }
    if job_id:
        payload["job_id"] = int(job_id)
    if project_id:
        payload["project_id"] = int(project_id)
    print(payload)
    r = requests.post(
        "http://" + url + "/api/model/v1/gpumodel",
        json=payload,
        headers={"Digest": md5, "uid": uid, "uname": uname}
    )
    print(r)
    print(r.json())
    return r.json()
