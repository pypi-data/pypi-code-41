# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     merge
   Description :
   Author :        Asdil
   date：          2019/9/11
-------------------------------------------------
   Change Activity:
                   2019/9/11:
-------------------------------------------------
"""
__author__ = 'Asdil'
import os
import subprocess
from multiprocessing import Pool


# 合并两个目录
def pathJoin(path1, path2):
    assert type(path1) is str
    assert type(path2) is str
    if path1[-1] != '/':
        path1 += '/'
    if path2[0] == '/':
        path2 = path2[1:]
    return path1 + path2


# 获取目标目录文件
def getFiles(path, extension=None, key=None):
    if extension is not None:
        l = -len(extension)
        ret = [pathJoin(path, each) for each in os.listdir(path) if each[l:] == extension]
    elif key is not None:
        ret = [pathJoin(path, each) for each in os.listdir(path) if key in each]
    else:
        ret = [pathJoin(path, each) for each in os.listdir(path)]
    return ret


def subprocessCall(cmd):
    subprocess.call(cmd, shell=True)


def subprocessCheckAll(cmd):
    subprocess.check_call(cmd, shell=True)


def unzip(path):
    path = pathJoin(path, '*.gz')
    cmd = f'gunzip {path}'
    subprocessCall(cmd)


def delHead(path):
    cmd = f'grep -v "#" {path} > {path}_'
    subprocessCheckAll(cmd)
    return f'{path}_'


def merging(paths, out_path):
    paths = ' '.join(paths)
    cmd = f'cat {paths} > {out_path}'
    subprocessCheckAll(cmd)


def delFiles(paths):
    paths = ' '.join(paths)
    cmd = f'rm -rf {paths}'
    subprocessCheckAll(cmd)


def mergeProcess(paths, out_path):
    if out_path == None:
        out_path = '/'.join(paths[0].split('/')[:-1]) + '/merge.vcf'
    newpaths = [paths[0]]

    for path in paths[1:]:
        path = delHead(path)  # 删除头文件
        newpaths.append(path)

    merging(newpaths, out_path)
    delFiles(newpaths[1:])
    print(f'合并成功,输出文件{out_path}')


def mergeVcf(dir_path, paths=None, out_path=None):
    if paths == None:
        unzip(dir_path)
        paths = getFiles(dir_path, 'vcf')
        chrom = [int(each.split('.')[-2]) for each in paths]  # 默认:  板子号.2.vcf
        paths = list(zip(chrom, paths))
        paths = sorted(paths, key=lambda x: x[0])  # 按照染色体排序
        paths = [each[1] for each in paths]
    mergeProcess(paths, out_path)


def hp():
    print("mergeVcf(dir_path, paths=None, out_path=None)")