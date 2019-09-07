# encoding:utf-8
import os
import sys

try:
    from py_ex import *
except:
    import logging
from PIL import Image


def _path_fmt(path):
    return path.replace("/", os.sep)


def resizeBatch(texture, sizelist, tarlist):
    img = Image.open(texture)
    index = 0
    tmpimg = {}
    for size in sizelist:
        tmpimg[index] = img.resize((size, size), Image.ANTIALIAS)

        path_base = os.path.split(tarlist[index])[0]
        if not os.path.isdir(path_base):
            os.mkdir(path_base)

        tmpimg[index].save(tarlist[index])
        logging.debug("Resize the image [%s] to [%s] (%s)" % (
            texture, tarlist[index], size))
        index = index + 1


def resizeSingle(texture, sizew, sizeh, tardir):
    img = Image.open(texture)
    img.resize((sizew, sizeh), Image.ANTIALIAS)

    path_base = os.path.splie(texture)[0]
    filename_base = os.path.splie(texture)[1]

    try:
        tarfile = os.path.join(tardir, filename_base)
        if os.path.isfile(tarfile):
            os.remove(tarfile)
        ret.save(tarfile)
        logging.debug("Resize the Imgge [%s] to [%s]" % (texture, tardir))
    except:
        logging.error("@!Save texture failed")


def pack_platicon(basetexture, topath, platform="android"):
    if platform == "android":
        sizelist = [72, 72, 36, 48, 96, 144]
        pathlist = [_path_fmt(topath + "/drawable/icon.png"), _path_fmt(topath + "/drawable-hdpi/icon.png"), _path_fmt(topath + "/drawable-ldpi/icon.png"),
                    _path_fmt(topath + "/drawable-mdpi/icon.png"), _path_fmt(topath + "/drawable-xhdpi/icon.png"), _path_fmt(topath + "/drawable-xxhdpi/icon.png")]
        resizeBatch(basetexture, sizelist, pathlist)

    elif platform == "ios":
        sizelist = [29, 36, 40, 48, 50, 57, 58, 72, 76, 80, 87,
                    96, 100, 114, 120, 121, 144, 152, 167, 180, 181, 512]
        tarlist = ["Icon-29.png", "Icon-36.png", "Icon-40.png", "Icon-48.png", "Icon-50.png",
                   "Icon-57.png", "Icon-58.png", "icon-72.png", "Icon-76.png",
                   "Icon-80.png", "Icon-87.png", "Icon-96.png", "Icon-100.png",
                   "Icon-114.png", "Icon-120.png", "Icon-121.png", "Icon-144.png",
                   "Icon-152.png", "Icon-167.png", "Icon-180.png", "Icon-181.png", "Icon-512.png"]
        reltarlist = []
        for iconname in tarlist:
            reltarlist.append(_path_fmt(topath + "/%s" % iconname))

        resizeBatch(basetexture, sizelist, reltarlist)
