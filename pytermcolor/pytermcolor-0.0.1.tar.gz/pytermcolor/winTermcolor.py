
"""Windows Color formatting for output in terminal.
http://code.activestate.com/recipes/496901-change-windows-console-character-attribute-color/
"""

from __future__ import print_function

from pytermcolor import COLORS, HIGHLIGHTS, ATTRIBUTES
import ctypes

import ctypes.wintypes
from ctypes import windll
from ctypes import (
        byref, Structure, c_char, c_short, c_uint32, c_ushort
    )


class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
    _fields_ = [
        ('dwSize', ctypes.wintypes._COORD),
        ('dwCursorPosition', ctypes.wintypes._COORD),
        ('wAttributes', ctypes.c_ushort),
        ('srWindow', ctypes.wintypes._SMALL_RECT),
        ('dwMaximumWindowSize', ctypes.wintypes._COORD)
    ]

STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE= -11
STD_ERROR_HANDLE = -12

FOREGROUND_BLUE = 0x01 # text color contains blue.
FOREGROUND_GREEN= 0x02 # text color contains green.
FOREGROUND_RED  = 0x04 # text color contains red.
FOREGROUND_INTENSITY = 0x08 # text color is intensified.
BACKGROUND_BLUE = 0x10 # background color contains blue.
BACKGROUND_GREEN= 0x20 # background color contains green.
BACKGROUND_RED  = 0x40 # background color contains red.
BACKGROUND_INTENSITY = 0x80 # background color is intensified.

std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

FORE_COLOR = {
    "grey": FOREGROUND_INTENSITY,
    "red": FOREGROUND_RED,
    "green": FOREGROUND_GREEN,
    "yellow": FOREGROUND_GREEN | FOREGROUND_RED,
    "blue": FOREGROUND_BLUE,
    "magenta": FOREGROUND_BLUE | FOREGROUND_RED,
    "cyan": FOREGROUND_BLUE|FOREGROUND_GREEN,
    "white": FOREGROUND_BLUE|FOREGROUND_GREEN |FOREGROUND_RED
}

BACK_COLOR = {
    "grey": BACKGROUND_INTENSITY,
    "red": BACKGROUND_RED,
    "green": BACKGROUND_GREEN,
    "yellow": BACKGROUND_GREEN | BACKGROUND_RED,
    "blue": BACKGROUND_BLUE,
    "magenta": BACKGROUND_BLUE | BACKGROUND_RED,
    "cyan": BACKGROUND_BLUE|BACKGROUND_GREEN,
    "white": BACKGROUND_BLUE|BACKGROUND_GREEN |BACKGROUND_RED
}


def GetConsoleScreenBufferInfo():
    handle = std_out_handle
    csbi = CONSOLE_SCREEN_BUFFER_INFO()
    success = windll.kernel32.GetConsoleScreenBufferInfo(
        handle, byref(csbi))
    # print(csbi.wAttributes)
    return csbi.wAttributes


def set_color(color, handle=std_out_handle):
    """
    Sets the terminal color

    Example: set_color(FOREGROUND_GREEN | FOREGROUND_INTENSITY)
    """

    attrib = GetConsoleScreenBufferInfo()
    b = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
    return attrib


def reset(attribute, handle=std_out_handle):
    ctypes.windll.kernel32.SetConsoleTextAttribute(handle, attribute)


def win_cprint(text, color=None, back_color=None):
    """
    Print colorized text with with windows api
    Available text and background colors:
        red, green, yellow, blue, magenta, cyan, white.
    :param text: the text to colorize
    :type text: str
    :param color: the color of the text
    :type color: str
    :param back_color: background color
    :type back_color: str
    :return: the text
    :rtype: str
    """
    att = 0
    if color is not None:
        att |= FORE_COLOR[color]

    if back_color is not None:
        att |= BACK_COLOR[back_color]

    # print(att)
    if att != 0:
        attrib = set_color(att)
    print(text)
    if att != 0:
        reset(attrib)
    return text
