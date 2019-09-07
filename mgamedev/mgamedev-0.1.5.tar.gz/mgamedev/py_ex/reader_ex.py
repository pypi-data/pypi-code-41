#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# Read simple data file ex: json // xml // plist //  zip
# ----------------------------------------------------------------------------
import os

# public functions
# ============================comman==============================
# 读取文件的md5


def getFileMd5(filepath):
    import hashlib
    m5 = hashlib.md5()
    data = file(filepath, "rb")
    while True:
        b = data.read(1024)
        if not b:
            break
        m5.update(b)
    data.close()
    return m5.hexdigest()

# ============================json=================================
# 读取json文件 返回一个字典


def readJsonFile(filename, mod="r+"):
    import json
    f = file(filename, mod)
    ret = json.loads(f.read().decode("utf-8"))
    f.close()
    return ret

# ============================plist===============================


def readPlistFile(filename):
    import plistlib
    pl = plistlib.readPlist(filename)
    return pl

# ============================xml=================================
# 读取Android的value文件夹下的string.xml文件


def readAndroid_stringxml(file, valuestring):
    from xml.etree import ElementTree
    root = ElementTree.parse(file)

    list_children = root.getiterator("resources")
    for node in list_children:
        print(node)
        if node.tag == "resources":
            for item in node:
                if item.tag == "string":
                    item.text = valuestring

# ===========================zip==================================
# 解压一个zip文件到制定目录


def unzipFile(zippath, tarpath=os.path.join(os.getcwd())):
    import zipfile
    import shutil

    if not os.path.isdir(tarpath):
        os.mkdir(tarpath)

    # unzip to download tarpath
    unzipobj = zipfile.ZipFile(zippath, 'r')
    zipname = os.path.split(zippath)[1]
    downpath = os.path.join(tarpath, os.path.splitext(zipname)[0])
    for filename in unzipobj.namelist():
        filepath = os.path.join(tarpath, filename)
        filepath = filepath.replace("/", '\\')

        # path
        if filepath.endswith("\\"):
            filepath = filepath[:-1]
            if os.path.isdir(filepath):
                shutil.rmtree(filepath)
            os.mkdir(filepath)
            print("unzip the dir %s " % filepath)
        # file
        else:

            path_file = os.path.split(filepath)[0]
            if not os.path.isdir(path_file):
                os.mkdir(path_file)

            data = unzipobj.read(filename)
            fileobj = open(filepath, "w+b")
            fileobj.write(data)
            print("unzip the file %s " % fileobj)
            fileobj.close()

    unzipobj.close()
