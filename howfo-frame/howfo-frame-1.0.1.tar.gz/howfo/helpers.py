# -*- coding: utf-8 -*-
"""
    howfo.helpers
    Implements various helpers.
    :copyright: 2019 Kalaiya86
    :license: MIT License
"""

import os


# 文件夹及文件处理

def tpl_path():
    """Get the project path, indicated by the
    :envvar:`TPL_PATH` environment variable. The default is
    ``'app'``.
    """
    tpl_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(tpl_path, 'tpl') or "tpl"

def config_path():
    """Get the project path, indicated by the
    :envvar:`TPL_PATH` environment variable. The default is
    ``'app'``.
    """
    config_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(config_path, 'config') or "config"


def base_path(name=None):
    """Get the project path, indicated by the
    :envvar:`BASE_PATH` environment variable. The default is
    ``'app'``.
    """
    root = os.path.dirname(os.path.abspath(__file__))
    if name:
        root = os.path.join(root, name)
    return os.environ.get("BASE_PATH") or root


def mk_dir(path):
    # 创建文件夹
    # 去除首尾空格
    path = path.strip()

    # 判断路径是否存在 存在 True 不存在False
    folder = os.path.exists(path)

    # 判断结果
    if not folder:
        # 不存在创建目录
        os.makedirs(path)
        print(path + '目录创建成功')
        return True
    else:
        # 如果已存在直接返回
        return False


def mk_file(path, name, new_template=''):
    # 创建文件
    make_template_path = path + name
    if not os.path.isfile(make_template_path):
        with open(make_template_path, 'w+', encoding='utf-8') as f:
            f.write(new_template)
        print(make_template_path + '文件创建成功')
        return True
    else:
        # 如果已存在直接返回
        print(make_template_path + '文件创建失败或者已经存在')
        return False


def mk_folder(structure, full_path):
    # print(f, basepath)
    # 循环创建目录和文件
    for item in structure:
        name = item.get('name')
        is_folder = item.get('is_folder')
        child = item.get('child')
        current_path = os.path.join(full_path, name)
        print(current_path, is_folder, child)
        if is_folder:
            mk_dir(current_path)
            mk_folder(child, current_path)
        else:
            tpl_name = item.get('content')
            tpl_paths = os.path.join(tpl_path(), tpl_name)
            print('80', tpl_paths)
            tpl_content, is_json = load_file(tpl_paths)
            mk_file(current_path, '', tpl_content)


def load_file(path, to_json=False):
    """
        取得json文件内容
        to_json: 加载成json形式
    """
    import json
    # path_list = path.split('.')
    is_json = True if path.split('.')[-1] == 'json' else False
    print('91', is_json)
    if not os.path.exists(path):
        content = {} if to_json else ''
    else:
        with open(path, "r", encoding='UTF-8') as f:
            if is_json and to_json:
                content = json.load(f)
            else:
                content = f.read()

    return content, is_json


def create_app(name, path):
    """
        创建app
    """
    app_path = os.path.join(path, name)
    print(app_path)

    json_path = os.path.join(config_path(), 'structure.json')
    structure, is_json = load_file(json_path, True)
    #print(structure)
    mk_folder(structure, app_path)


def folder_files(folder_path, rule='*.*'):
    """
        取得文件夹下所有文件
    """
    from fnmatch import fnmatch
    folder_all_file = os.listdir(folder_path)
    folder_all_file.sort(key=lambda x: x.__contains__('.'))
    files = [name for name in folder_all_file if fnmatch(name, rule)]
    return files


# 数据处理
def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        if type(dictionary) == dict:
            result.update(dictionary)
    return result


def get_uuid(kind):
        import uuid
        if kind == 'Time':
            return str(uuid.uuid1())
        elif kind == 'Random':
            return str(uuid.uuid4())
        else:
            return str(uuid.uuid4())


def get_env():
    conf_path = config_path()
    env_status = ''
    for filename in os.listdir(conf_path):
        env_file = os.path.splitext(filename)[0]
        if env_file == 'development':  # 开发环境
            env_status = 'development'
            break
        elif env_file == 'testing':  # 测试环境
            env_status = 'testing'
            break
        elif env_file == 'preview':  # 预生产环境
            env_status = 'preview'
            break
        elif env_file == 'local':
            env_status = 'local'
            break
        else:
            env_status = 'product'  # 生产环境 默认的
    return env_status
