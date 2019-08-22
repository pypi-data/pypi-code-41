
"""ANSI Color formatting for output in terminal."""

from __future__ import print_function

from pytermcolor import COLORS, HIGHLIGHTS, ATTRIBUTES


RESET = '\033[0m'


def ansi_colored(text, color=None, back_color=None, attrs=None):
    """
    Colorize text with ANSI codes
    Available text and background colors:
        red, green, yellow, blue, magenta, cyan, white.
    :param text: the text to colorize
    :type text: str
    :param color: the color of the text
    :type color: str
    :param back_color: background color
    :type back_color: str
    :param attrs: text attribute
        Available attributes:
            bold, dark, underline, blink, reverse, concealed.
    :type attrs: str
    :return: the ansi colored text
    :rtype: str
    """
    fmt_str = '\033[%dm%s'
    if color is not None:
        text = fmt_str % (COLORS[color], text)

    if back_color is not None:
        text = fmt_str % (HIGHLIGHTS[back_color], text)

    if attrs is not None:
        for attr in attrs:
            text = fmt_str % (ATTRIBUTES[attr], text)

    text += RESET

    return text







