# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on MAY 21, 2018
@author: zhanglanhui
homepage recommender:ffm
"""
import os


def file_repalce(source, dest):
    os.replace(source, dest)


def get_dir_path(file):
    return os.path.abspath(os.path.dirname(file))


def get_updir_path(file):
    return os.path.dirname(os.path.dirname(os.path.abspath(file)))


def get_upupdir_path(file):
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(file))))
