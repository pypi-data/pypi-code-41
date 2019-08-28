#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'bee'
import qrcode,os
from PIL import Image, ImageFont, ImageDraw

# 制作二维码
def create_qrcode(url="", color="#000000"):
    image = qrcode.make(url)
    image = image.convert("RGBA")
    datas = image.getdata()
    newData = []
    # print(color)
    color = toRgb(color)
    # print(color)
    for item in datas:
        if item[0] == 0 and item[1] == 0 and item[2] == 0:
            item = color
            newData.append(item)
        else:
            newData.append(item)
    image.putdata(newData)
    return image


# 合并二维码，生成带用户名和二维码的转介图片
# 返回image对象
def merge_img(referral_base_path, qrcode_img, qrcode_pos, qrcode_size):
    if not referral_base_path:
        return 1, u'没有图片', None

    try:
        referral_img = Image.open(referral_base_path)
        qrcode_img = qrcode_img.resize(qrcode_size, Image.ANTIALIAS)
        referral_img.paste(qrcode_img, qrcode_pos)

    except Exception as e:
        return 1, str(e), None
    return 0, '', referral_img


def toRgb(qrcode_color):
    import re
    qrcode_color = qrcode_color.replace('#', '')
    opt = re.findall(r'(.{2})', qrcode_color)  # 将字符串两两分割
    color_tuple = ()  # 用以存放最后结果
    for i in range(0, len(opt)):  # for循环，遍历分割后的字符串列表
        t = (int(opt[i], 16),)
        color_tuple += t  # 将结果拼接成12，12，12格式
    # print("转换后的RGB数值为：")
    color_tuple += (255,)
    return color_tuple