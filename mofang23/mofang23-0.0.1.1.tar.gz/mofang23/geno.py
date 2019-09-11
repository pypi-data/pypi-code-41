# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     geno
   Description :
   Author :        Asdil
   date：          2019/5/8
-------------------------------------------------
   Change Activity:
                   2019/5/8:
-------------------------------------------------
"""
__author__ = 'Asdil'
import pandas as pd


# 识别过滤的行数
def skipRow(path, key):
    skip = 0
    with open(path, 'r') as f:
        for line in f:
            if key == line[:len(key)]:
                return skip
            skip += 1
    return skip


# 读取call文件
def readCall(path, key='probeset_id'):
    df = pd.read_table(path, skiprows=skipRow(path, key), low_memory=False)
    return df


# 读取vcf
def readVcf(path, key='#CHROM'):
    df = pd.read_table(path, skiprows=skipRow(path, key), low_memory=False)
    return df
