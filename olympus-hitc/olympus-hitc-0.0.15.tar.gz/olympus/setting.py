# coding=utf-8

import os
import platform

# 从容器环境变量中初始化相关信息
md5 = os.getenv("MD5")
# 当前登录用户的ID
uid = os.getenv("UID")
# 当前登录用户的用户名
uname = os.getenv("UName")
# gateway地址
url = os.getenv("gateway_url")
# 训练Job的ID
job_id = os.getenv("jobId")
# 训练Job所属的ProjectID
project_id = os.getenv("projectId")
# 训练生成的模型文件在GlusterFS上的绝对路径
host_path = os.getenv("py_hostpath")
# 训练生成的模型文件在容器内的相对路径
container_path = os.getenv("py_containerpath")


def search_hitc_path():
    plm = platform.system()

    if plm == "Windows":

        env_dist = os.environ["Path"].split(";")
     
        for st in env_dist:

            if os.path.exists(st) and os.path.isdir(st):
                if "hitc.exe" in os.listdir(st):
                    # print ("check you hitc.exe exist!".upper())
                    return os.path.join(st,"hitc.exe")

        print ("please append you hitc.exe on you Windows system Path".upper())

    else:
        env_dist = os.environ["PATH"].split(":")
     
        for st in env_dist:
            if os.path.exists(st) and os.path.isdir(st):
                if "hitc" in os.listdir(st):
                    # print ("check you hitc exist!".upper())
                    return os.path.join(st,"hitc")

        print ("please append you hitc on you Linux system Path".upper())
    return None


HITC_PATH = search_hitc_path()

