#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Version : python3.6
@Author  : LiuSQ
@Time    : 2019/9/5 11:06
@Describe: 
"""

class TextHelper:
    """
        中安文本处理工具类
    """
    def __init__(self):
        pass

    @staticmethod
    def get_num_in_text(text=""):
        """
            获取权限弹窗的个数
        :param text:
        :return:
        """
        text_other = text.strip().split("共")[1].split("项")[0].strip(" ")
        print(text_other)
        return text_other


if __name__ == "__main__":
    TextHelper.get_num_in_text("第 2 项权限（共 3 项）")
