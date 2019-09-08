# -*- coding:utf-8 -*-
"""
Hello from Tools/Common/Font.py
"""

import glob
import os


def WinGetSysFonts():
    """
    Get all .ttf fonts on Windows system.

    Returns
    -------
    list
        It's a list of all .ttf font names.
    """
    font_abs_paths = glob.glob(r"C:\Windows\Fonts\*.ttf")
    font_names = []

    for font_abspath in font_abs_paths:
        font_names.append(os.path.splitext(font_abspath.split("\\")[-1])[0])

    return font_names


def Demo():
    """This function is a demo of all functions and classes in this module."""
    for font in WinGetSysFonts():
        print(font)


if __name__ == '__main__':
    Demo()
