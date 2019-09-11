#coding: utf8
from __future__ import absolute_import
import os
import time
import sys
import re

from xserver.utils import unicode

is_win = sys.platform == 'win32'
is_mac = sys.platform == 'darwin'
is_linux = 'linux' in sys.platform.lower()



def make_sure_path(path, is_file=False, is_dir=False):
    # 保证path是有效的，特别是写入一个文件的时候，避免没有父目录，而写入失败
    # 如果返回False，表示有问题...
    # is_file 表示会新建一个文件，里面用当前的时间戳作为正文内容
    if not is_dir: # 非 dir，只保证其父目录的存在
        folder, name = os.path.split(path)
    else:
        folder = path
    if not os.path.isdir(folder):
        try:
            os.makedirs(folder)
        except:
            return False
    if is_file: # like touch in linux
        try:
            with open(path, 'w') as f:
                f.write("%s" % time.time())
        except:
            pass
    return True




def get_home_path():
    home_path = ''
    if os.environ.get('HOME'):
        home_path = os.environ['HOME']
        if not os.path.exists(home_path):
            home_path = ''
    if not home_path:
        home_path = ''
        if is_mac or is_linux:
            current_user = os.getlogin()
            home_path = '/Users/%s' % current_user
    return  home_path



def write_file(filepath, content):
    make_sure_path(filepath)
    if isinstance(content, unicode):
        content = content.encode('utf8')
    with open(filepath, 'wb') as f:
        f.write(content)


def read_file(filepath):
    if not os.path.isfile(filepath):
        return ''
    else:
        with open(filepath, 'rb') as f:
            raw_content = f.read()
        return raw_content


def get_relative_path(filepath, root, return_name_if_fail=True):
    if filepath and root and filepath.startswith(root+'/'):
        return filepath.replace(root, '').strip('/')
    elif filepath == root:
        return ''
    else:
        if return_name_if_fail:
            return os.path.split(filepath)[-1]
        else:
            return filepath



def is_real(path):
    # 主要是判断是否真实的文档，还是软链，或者软链下的目录内
    if not os.path.exists(path):
        return False
    parts = path.split('/')
    for i in range(len(parts)):
        if i:
            _path = '/'.join(parts[:-i])
        else:
            _path = path
        if os.path.islink(_path):
            return False
    return True


def is_a_hidden_path(path):
    if re.search('(^|/)(\.|~$)', path):
        return True
    elif re.search(r'~\.[^.]+$', path):
        return True
    elif path.endswith('~'):
        return True
    else:
        return False


def get_file_list(root_path, split=False):
    # 遍历folder
    file_paths = []
    just_files = []
    just_folders = []
    if not os.path.isdir(root_path): # 根目录不存在，不处理
        pass
    else:
        for parent, folders, files in os.walk(root_path):
            if is_a_hidden_path(parent):
                continue
            elif not is_real(parent): # link类型的不处理
                continue

            for filename in files:
                file_path = os.path.join(parent, filename)
                if not is_a_hidden_path(file_path) and is_real(file_path):
                    #relative_path = file_path.replace(root_path, '').strip('/')
                    file_paths.append(file_path)
                    just_files.append(file_path)

            for filename in folders:
                file_path = os.path.join(parent, filename)
                if not is_a_hidden_path(file_path) and is_real(file_path):
                    #relative_path = file_path.replace(root_path, '').strip('/')
                    file_paths.append(file_path)
                    just_folders.append(file_path)
    if not split:
        return file_paths
    else:
        return just_folders, just_files