#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# Write dict to file ex: json // xml // plist //  zip
# ----------------------------------------------------------------------------
import os

# common functions
#============================common=================================


def write2XXTeaFile(strvalue, tarfile, key):
    from lib import *
    fobj = file(tarfile, 'w+')
    fobj.write(xxtea.encrypt(strvalue, key))
    fobj.close()

# public functions
#============================json=================================
# 写入json文件


def write2Json(dict, tarfile, mod="w+"):
    import json
    jsonobj = open(tarfile,  mod)  # json-file
    json.dump(dict, jsonobj, sort_keys=True, indent=4)
    jsonobj.close()


#===========================zip==================================
# 压缩一个文件夹到指定zip
# 把整个文件夹内的文件打包
def write2Zip(zippath, tarfile):
    import zipfile
    filelist = []
    if os.path.isfile(zippath):
        filelist.append(zippath)
    else:
        for dirpath, dirnames, filenames in os.walk(zippath):
            for filename in filenames:
                filelist.append(os.path.join(dirpath, filename))

    f = zipfile.ZipFile(tarfile, 'w', zipfile.ZIP_DEFLATED)
    for tar in filelist:
        arcname = tar[len(zippath):]
        f.write(tar, arcname)
    f.close()
