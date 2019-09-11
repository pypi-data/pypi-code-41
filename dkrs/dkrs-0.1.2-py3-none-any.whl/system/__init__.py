# Copyright (C) 2019 Erhu Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import hashlib
import os
import platform
import time
from sys import stdin

from dkrs.log import log


def os_system(cmd, with_output=True):
    """
    执行 os.system(cmd)
    :param cmd: 命令
    :param with_output: 是否输出执行过程
    :return: True:执行成功, False:执行失败
    """
    if with_output:
        return os.system(cmd) == 0
    else:
        return os.system('{cmd} > /dev/null 2>&1'.format(cmd=cmd)) == 0


def os_system_tip(cmd, tip='', with_output=True):
    """
    执行 os.system(cmd)
    :param cmd: 命令
    :param tip: 提示语
    :param with_output: 是否输出执行过程
    :return: True:执行成功, False:执行失败
    """
    result = os_system(cmd, with_output)
    r_tip = cmd if tip.strip() == '' else tip
    log('{tip} {msg}'.format(tip=r_tip, msg='' if result else '[失败]'))
    return result


def os_popen(cmd):
    """
    执行 os.system(cmd)，返回执行结果
    """
    return os.popen(cmd).read()


def get_user_input(prompt, options=None, default=None, cond_fun=None, cond_tip=None):
    """
    获取用户输入
    :param prompt: 提示语
    :param options: 可选项
    :param default: 默认值
    :param cond_fun: 检查用户输入是否满足条件的函数
    :param cond_tip: 不满足条件时的提示语
    :return:
    """
    if options is None:
        options = []
    inner_status = 0
    while inner_status != -1:
        log('{}: '.format(prompt))
        cmd = stdin.readline().strip()

        # 有默认值
        if default and cmd == '':
            return default

        # 无默认值
        if cmd == '':
            continue
        # 退出
        if cmd in [':Q', ':q']:
            inner_status = -1
        else:
            # 有选项 且 用户输入未在选项中
            if len(options) > 0 and cmd not in options:
                log('[Error] {} 是无效选项，有效选项为 {}\n'.format(cmd, options))
                continue

            # 无选项 或者 用户输入在选项中
            # 有检查条件
            if cond_fun:
                # 满足条件
                if cond_fun(cmd):
                    return cmd
                else:
                    log('{}'.format(cond_tip))
                    continue
            else:
                return cmd
    return None


def file_sha256(file_name):
    """
    取文件的 sha 256
    :param file_name: 文件路径
    """
    algorithm = hashlib.sha256()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            algorithm.update(chunk)
    return algorithm.hexdigest()


def md5(a_str):
    """
    获取字符串的 MD5
    :param a_str: 字符串
    """
    import hashlib
    return hashlib.md5(a_str.encode('utf-8')).hexdigest()


def os_is_windows():
    """
    是否是 windows 系统
    """
    return platform.system() == 'Windows'


def gradlew():
    """
    根据当前系统，获得 gradlew 命令
    """
    if os_is_windows():
        return '.\\gradlew.bat '
    else:
        return './gradlew '


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def timestamp():
    return int(round(time.time() * 1000))
