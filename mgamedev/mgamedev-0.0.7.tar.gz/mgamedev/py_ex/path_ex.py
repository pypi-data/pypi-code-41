# encoding:utf8
# !/usr/bin/env python

import os
import sys
import shutil


def add_path_prefix(path_str):
    """ Compatible windows-sys filepath """
    if sys.platform != "win32":
        return path_str

    if path_str.startswith("\\\\?\\"):
        return path_str

    ret = "\\\\?\\" + os.path.abspath(path_str)
    ret = ret.replace("/", "\\")
    return ret


def get_dirname(path):
    """ Get current path dirname. """
    if not os.path.isdir(path):
        return
    tmp = path.split("\\")
    name = tmp[len(tmp) - 1]
    return name


def copy_dirfiles_to(fromdir, todir):
    """ Copy all files from $fromdir to $todir|both path must exist! """
    if not os.path.isdir(todir):
        os.makedirs(todir)
    for item in os.listdir(fromdir):
        path = os.path.join(fromdir, item)
        if os.path.isfile(path):
            path = add_path_prefix(path)
            copy_dst = add_path_prefix(todir)
            shutil.copy(path, copy_dst)
        if os.path.isdir(path):
            new_dst = os.path.join(todir, item)
            if not os.path.isdir(new_dst):
                os.makedirs(add_path_prefix(new_dst))
            copy_dirfiles_to(path, new_dst)


def re_pathfile_postifix(path, beflist, tolist):
    """ Change all file-postifix $beflist to $tolist """
    newname = ""
    for typename in beflist:
        for filename in os.listdir(path):
            item = os.path.join(path, filename)
            if os.path.isfile(item) and os.path.basename(filename).find(typename) != -1:
                newname = tolist[beflist.index(typename)]
                os.rename(item, newname)
            if os.path.isdir(item):
                re_pathfile_postifix(item, beflist, tolist)


def del_postifix_files(path, typelist):
    """ Del all file end with $typelist's postifix """
    for typename in typelist:
        for filename in os.listdir(path):
            item = os.path.join(path, filename)
            if os.path.isfile(item) and os.path.basename(filename).find(typename) != -1:
                os.remove(item)
            if os.path.isdir(item):
                del_postifix_files(item, typelist)
