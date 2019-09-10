# -*- coding:utf-8 -*-
import os, sys
from os import listdir
from os.path import isfile, isdir, join as path_join
from zipfile import ZipFile
from acumos.pickler import AcumosContextManager, load_model as _load_model


def _infer_model_dir(path):
    '''Returns an absolute path to the model dir. Unzips the model archive if `path` contains it'''
    model_zip_path = path_join(path, 'model.zip')
    if isfile(model_zip_path):
        model_dir = path_join(path, 'model')
        zip_file = ZipFile(model_zip_path)
        zip_file.extractall(model_dir)
    else:
        model_dir = path

    return model_dir


def _extend_syspath(context):
    '''Adds user-provided packages to the system path'''
    provided_abspath = context.build_path(path_join('scripts', 'user_provided'))
    if provided_abspath not in sys.path:
        sys.path.append(provided_abspath)

    for pkg_name in listdir(provided_abspath):
        pkg_abspath = path_join(provided_abspath, pkg_name)
        if not isdir(pkg_abspath):
            continue

        if pkg_abspath not in sys.path:
            sys.path.append(pkg_abspath)


def load_model(path):
    model_dir = _infer_model_dir(path)
    with AcumosContextManager(model_dir) as c:
        _extend_syspath(c)  # extend path before we unpickle user model
        with open(c.build_path('model.pkl'), 'rb') as f:
            model = _load_model(f)
    os.system('rm -rf ' + model_dir)
    return model



path = 'out/多语言翻译V1'
model = load_model(path)

result = model.translate.inner(['zh-cn', 'ja', '今晚的夜色真美！'])
print(result)
