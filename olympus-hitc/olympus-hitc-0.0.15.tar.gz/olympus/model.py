# coding=utf-8
"""
    针对调用命令行的算法模型创建的一个类

"""
from __future__ import print_function

import os
import sys
import re

import time
import json
import platform
import requests

from olympus.utils import hitc,hitcx



# 检测核对save接口,不确定类型参数的格式是否合格
def parsing_args(**kw):
    if kw.get("json_path") is None:
        return None

    json_path=  kw["json_path"]

    if isinstance(json_path,str):
        models_cnt = 1

    elif isinstance(json_path,list) :
        models_cnt = len(json_path)
    else:
        return False


    for k, _arg in kw.items():
        if not _arg:
            kw[k] = [_arg for _ in range(models_cnt)]
            # continue

        elif isinstance(_arg ,str):
            kw[k] = [_arg for _ in range(models_cnt)]
            
        elif isinstance(_arg ,list) and len(_arg) == models_cnt:
            continue
        
        elif isinstance(_arg,list) and len(_arg) != models_cnt:
            print (u"len(%s) != len() check you args..." % k)
            return False

    return kw

class Model(object):
    '''
        定义一个算法模型创建，版本添加,下载,删除的类
    '''
    def __init__(self):
        super(Model, self).__init__()


    def save(self, name, task_type, json_path , param_path, dept,\
                    level=None, framework=None, usage=None, commit_message=None, version=None,\
                    logurl=None, desc=None, view_flag=False):
        """
            creat一个模型，并且支持append多个版本

            Return success or fail or error.

            Parameters 参数如果都是字符串就创建一条,如果是列表就创建多个版本,参数列表位置对应 长度对齐
            ----------
            name       : set gpu model name
            task_type  : set gpu model's tasktype, currently support detection|classification|
                         segmentation|landmarks|skeleton|face recognition|person re-identification|
                         multi-object tracking|face anti-spoofing|traffic lane|multitask|head_pose
            
            json_path  : set a str or a list of gpu model 
                            for MXNet, set gpu model json file; 
                            for TensorFlow, set gpu model pb file; 
                            for PyTorch, set gpu model pt or pth file
                        ***hdfs://hobot-bigdata/user/jing01.wang/model/model_v2.10.2.json

            param_path : set a str or a list of gpu model                     
                            for MXNet, set gpu model json file; 
                            for TensorFlow, set ""; 
                            for PyTorch, set "";

                        ***hdfs://hobot-bigdata/user/jing01.wang/model/model_v2.10.2.params

            dept       : set department for gpu model
            level      : set gpu model permission,currently support private|
                         public,optional (default "private")

            framework  : set a str or a list of gpu model's framework, currently support MXNet|
                         TensorFlow|PyTorch (default "MXNet")

            usage      : set a str or a list of gpu model's usage, currently support for inference|
                         for compile|others (default "for inference")

            commit_message : set this version's commit message, optional
            version   : set gpu model's version in format like 'v0.1.0', automatic incre Patch if empty



            view_flag   ： 此参数可见所有模型和详情 view_flag = True 
                

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

            frameworks = ["MXNet","TensorFlow", "MXNet"]
            usages = ["for inference","MXNet","for inference"]

            for x in range(3):

                json_paths.append(json_path)
                param_paths.append(param_path)

            # 前五个参数是必填的参数
            # model.save(name, task_type, json_path, param_path, dept)

            # 五个以后的参数是非必填的参数,可以按顺序来一一填写
            # model.save(name, task_type, json_path, param_path, dept,\
            #                             level, framework, usage, commit_message,\
            #                             version, logurl, desc, view_flag=True
            #                             )
    
            # 五个以后的参数可以通过指定参数名称来选填,json_paths,param_paths,framework,usage"可以填写字符串,也可以填写列表
            # model.save(name, task_type, json_paths, param_paths, dept, framework = framework, usage = "for inference", version = "0.0.99")

            # 参数如果都是字符串就创建一条,如果是列表就创建多个版本，并且参数列表位置一一对应 长度对齐
            # model.save(name, task_type, json_paths, param_paths, dept, framework = frameworks, usage = usages, view_flag=True)




        """
        result = True
        begin = 0
        parent_id = None
        models_cnt = 0
        
        # 创建类型不确定的参数字典
        args_dct = {
                     "json_path": json_path, 
                     "param_path": param_path,
                     "framework": framework,
                     "usage": usage, 
                    }

        # 对参数传入的参数做对齐处理
        _args =  parsing_args(**args_dct)

        
        if not _args:
            return False


        res = self._save_one(
                name, task_type, _args["json_path"][0] , _args["param_path"][0], dept,\
                level, _args["framework"][0], _args["usage"][0], commit_message, version,\
                logurl, desc
                )


        if res.startswith("success") and re.search(r'\d+', res):
            # success, created gpu model dir's id is 237"
            parent_id = re.search(r'\d+', res).group()

            begin = 1         
            print (res)

        else:
            print (res)
            return False
        

        for json_path, param_path, framework, usage in zip(
                                            _args["json_path"][begin:],
                                            _args["param_path"][begin:],
                                            _args["framework"][begin:],
                                            _args["usage"][begin:],                                        
                                        ):
            if parent_id:
                # 多模型提交，add version时不能指定版本号，单独追加时可以
                res = self.append_one(parent_id, json_path, param_path, framework, usage, commit_message)

                if not res.startswith("success"):
                    result = False
                    print(res,'name:{}  task_type:{}  json_path:{}  param_path:{}  framework:{}  usage:{}\n'\
                        .format(name, task_type, json_path, param_path, framework, usage))


                   
        if view_flag and parent_id:
            print(self._get_detail(parent_id))

        return result


   

    def append_one(self, parent_id, json_path, param_path,\
                    framework=None, usage=None, commit_message=None, version=None):
        
        """
            给已存在的模型目录添加版本

            Return success or fail or error.

            Parameters
            ----------
            parent_id : parent_id is a known id 

            json_path : for MXNet, set gpu model json file; 
                        for TensorFlow, set gpu model pb file; 
                        for PyTorch, set gpu model pt or pth file
                        ***hdfs://hobot-bigdata/user/jing01.wang/model/model_v2.10.2.json

            param_path: set gpu model param file, only work for MXNet
                        ***hdfs://hobot-bigdata/user/jing01.wang/model/model_v2.10.2.params

            framework : set gpu model's framework, currently support MXNet|
                        TensorFlow|PyTorch (default "MXNet")

            usage     : set gpu model's usage, currently support for inference|
                        for compile|others (default "for inference")

            commit_message   : set this version's commit message, optional
            version   : set gpu model's version in format like 'v0.1.0', automatic incre Patch if empty


            Examples
            --------
            from olympus import model

            model = model.Model()

            parent_id = 266

            json_path = "C:\\Users\\v-yu.gao\\goworkpath\\olympus\\app\\cmd\\model_v2.10.2.json"
            param_path = "C:\\Users\\v-yu.gao\\goworkpath\\olympus\\app\\cmd\\model_v2.10.2.params"
            ***
                framework = "MXNet"
                json_path = "hdfs://hobot-bigdata/user/jing01.wang/model/model_v2.10.2.json"
                param_path = "hdfs://hobot-bigdata/user/jing01.wang/model/model_v2.10.2.params"

            ***
            ***
                framework = "TensorFlow"
                json_path = "hdfs://hobot-bigdata/user/jing01.wang/model/frozen_int_model.pb"
                param_path = ""

            ***
            usage = "for inference"

            model.append_one(parent_id, json_path, param_path, framework, usage)
        """

        # 命令行一共7个参数
        command = [
            "model", "append", "--id",str(parent_id), "-j", json_path,
        ]

        if not framework:
            framework = "MXNet"
        command.append(r'-f "%s"'%(framework))

        if framework == "TensorFlow" or framework ==  "PyTorch":
            param_path = ""


        if param_path is not None and param_path is not "":
            command.append(r'-p "%s"'%(param_path))


        if not usage: 
            usage = "for inference"
        command.append(r'-u "%s"'%(usage))


        if commit_message is not None:
            command.append(r'-m "%s"'%(commit_message))
       
        
        if version is not None:
            command.append(r'-v "%s"'%(version))


      
        return hitc(command)

   

    def download(self, idx):
        """
            算法模型单条下载
            Return success or fail or error.

            Parameters
            ----------
            idx     : idx is a known id
           

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
            return False

        elif res.startswith(
                "panic: interface conversion: interface {} is nil"):
            print (res)
            return False

        else:
            print("download model id %s " % str(idx))
            return True


    def delete(self, idx):
        """
            算法模型单条删除
            Return success or fail or error.

            Parameters
            ----------
            idx     : idx is a known id
           

            Examples
            --------
            from olympus import model

            model = model.Model()

            idx = 224
            model.delete(224) 


        """
        return hitcx(["model", "delete", "-k", str(idx)])



    # 创建单条模型,初始化相关参数
    def _save_one(self, name, task_type, json_path , param_path, dept,\
                    level=None, framework=None, usage=None, commit_message=None,\
                    version=None,logurl=None, desc=None):
    
        # 命令行一共12个参数
        command = [
            "model", "create", "-n", name, "-t", task_type, "-j", json_path, 
        ]

        if not framework:
            framework = "MXNet"
        command.append(r'-f "%s"'%(framework))

        if framework == "TensorFlow" or framework ==  "PyTorch":
            param_path = ""


        if param_path is not None and param_path is not "":
            command.append(r'-p "%s"'%(param_path))



        command.append(r'--dept "%s"'%(dept))

        if not level: 
            level = "private"
        command.append(r'--perm "%s"'%(level))

     

        if not usage: 
            usage = "for inference"
        command.append(r'-u "%s"'%(usage))


        if commit_message is not None:
            command.append(r'-m "%s"'%(commit_message))
       
        
        if version is not None:
            command.append(r'-v "%s"'%(version))


        if logurl is not None:
            command.append(r'-l "%s"'%(logurl))

        if desc is not None:
            command.append(r'-d "%s"'%(desc))


        return hitc(command)


    # 查看算法模型详情
    def _get_detail(self, idx):
        return hitc(["model", "get", "-k", str(idx)])
