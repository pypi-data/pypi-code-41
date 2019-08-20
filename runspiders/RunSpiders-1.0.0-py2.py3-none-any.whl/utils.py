# -*- coding: utf-8 -*-
# @Time     : 2019/8/19 17:56
# @Author   : Run 
# @File     : utils.py
# @Software : PyCharm

"""
1. 官方文档：
    会话对象让你能够跨请求保持某些参数。
    它也会在同一个Session实例发出的所有请求之间保持cookie，期间使用urllib3的connection pooling功能。
    所以如果你向同一主机发送多个请求，底层的 TCP 连接将会被重用，从而带来显著的性能提升。
2. 以下给出的两种方式request_url和get_http_session，都能实现对失败的请求再进行retry次尝试，但整体感觉session的方式速度更快一些。
"""

import requests
import requests.adapters
import time
import os
import stat
import shutil


def request_url(url, timeout=10, retry=3, retry_interval=0.1):
    """

    :param url:
    :param timeout:
    :param retry:
    :param retry_interval:
    :return:
        success: True, req
        fail: False, None
    """
    while retry:
        try:
            req = requests.get(url, timeout=timeout)
        except:
            retry -= 1
        else:
            if req.status_code == 200:
                return True, req
            else:
                retry -= 1
        time.sleep(retry_interval)
        return False, None


def get_http_session(pool_connections, pool_maxsize, max_retries):
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=pool_connections,
                                            pool_maxsize=pool_maxsize, max_retries=max_retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def delete_file(filePath):
    if os.path.exists(filePath):
        for fileList in os.walk(filePath):
            for name in fileList[2]:
                os.chmod(os.path.join(fileList[0],name), stat.S_IWRITE)
                os.remove(os.path.join(fileList[0],name))
        shutil.rmtree(filePath)
        return "delete ok"
    else:
        return "no filepath"


