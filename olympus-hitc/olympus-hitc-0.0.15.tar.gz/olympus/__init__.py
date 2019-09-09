# -*- coding: UTF-8 -*-
"""
	olympus-hitc
"""

import os
import platform
from olympus.utils import hitc
from olympus.setting import HITC_PATH

# 从容器环境变量中初始化相关信息
# md5 = os.getenv("MD5")
# # 当前登录用户的ID
# uid = os.getenv("UID")
# # 当前登录用户的用户名
# uname = os.getenv("UName")
# # gateway地址
# url = os.getenv("gateway_url")
# # 训练Job的ID
# job_id = os.getenv("jobId")
# # 训练Job所属的ProjectID
# project_id = os.getenv("projectId")
# # 训练生成的模型文件在GlusterFS上的绝对路径
# host_path = os.getenv("py_hostpath")
# # 训练生成的模型文件在容器内的相对路径
# container_path = os.getenv("py_containerpath")


def check_login():
    command = ["who"]
    res = hitc(command)
    ## Get login user info error:
    if res.startswith("You are not login"):
        command = ["login"]
        res = hitc(command)
    # print (res)


if HITC_PATH:
    check_login()