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

import platform

from dkrs.color import Colors


def log(msg):
    print(msg)


def error(msg, new_line=True):
    if platform.system() == 'Windows':
        log('[错误] {}'.format(msg))
        if new_line:
            log('')
    else:
        log(Colors.FAIL + '[错误] {}'.format(msg) + Colors.END)
        if new_line:
            log('')


def error2(msg):
    error(msg, False)


def info(msg, new_line=True):
    if platform.system() == 'Windows':
        log('[消息] {}'.format(msg))
        if new_line:
            log('')
    else:
        log(Colors.GREEN + '[消息] {}'.format(msg) + Colors.END)
        if new_line:
            log('')


def info2(msg):
    info(msg, False)


def warning(msg, new_line=True):
    if platform.system() == 'Windows':
        log('[警告] {}'.format(msg))
        if new_line:
            log('')
    else:
        log(Colors.WARNING + '[警告] {}'.format(msg) + Colors.END)
        if new_line:
            log('')


def warning2(msg):
    warning(msg, False)


def line():
    print('-----------------------------------------------')


def title(msg):
    line()
    log(msg)
    line()


def title_mid(msg):
    if platform.system() == 'Windows':
        log('\n----- {} -----\n'.format(msg))
    else:
        log(Colors.GREEN + '\n----- {} -----\n'.format(msg) + Colors.END)
