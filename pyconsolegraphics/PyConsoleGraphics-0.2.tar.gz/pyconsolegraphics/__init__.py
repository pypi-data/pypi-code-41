"""
PyConsoleGraphics is a "one size fits all" library for text-mode graphics.
It's designed to operate as a wrapper around the standard library curses
module, Pygame, and normal text output - enabling exactly the same code to run
under any supported backend on any supported system with no extra work on your
part. It also has wrappers around it, allowing drop-in replacement of other
console graphics libraries.

The MIT License (MIT)

Copyright (c) 2016 Schilcote

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import abc

import io
import random
import threading

import time

import sys

import collections

import math

import itertools
import weakref

import pyconsolegraphics.backends as backends

backend_attempt_order = ["pygamewindow"]
available_backends = set(backends.backend_funcs.keys())

keypress_code_set = {
    '!',
    '"',
    '#',
    '$',
    '&',
    "'",
    '(',
    ')',
    '*',
    '+',
    ',',
    '-',
    '.',
    '/',
    '0',
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
    '8',
    '9',
    ':',
    ';',
    '<',
    '=',
    '>',
    '?',
    '@',
    '[',
    '\\',
    ']',
    '^',
    '_',
    '`',
    'a',
    'b',
    'backspace',
    'c',
    'clear',
    'd',
    'delete',
    'down',
    'e',
    'end',
    'enter',
    'escape',
    'f',
    'f1',
    'f10',
    'f11',
    'f12',
    'f13',
    'f14',
    'f15',
    'f2',
    'f3',
    'f4',
    'f5',
    'f6',
    'f7',
    'f8',
    'f9',
    'g',
    'h',
    'i',
    'insert',
    'j',
    'k',
    'l',
    'left',
    'm',
    'n',
    'o',
    'p',
    'page down',
    'page up',
    'pause',
    'printscreen',
    'q',
    'r',
    'right',
    's',
    'space',
    'sysrq',
    't',
    'tab',
    'u',
    'up',
    'v',
    'w',
    'x',
    'y',
    'z',
    'shift',
    'control',
    'alt',
    'capslock',
    'numlock',
    'scrollock'
}

#Copied from Pygame's color names. It's very close to the X11 color name list
# - https://en.wikipedia.org/wiki/X11_color_names - but there's colors in there
# that aren't in this and there might be colors in this that aren't in there,
# I didn't check every single one..
colors = {'tomato3': (205, 79, 57, 255), 'deepskyblue2': (0, 178, 238, 255), 'slateblue2': (122, 103, 238, 255), 'skyblue4': (74, 112, 139, 255), 'navyblue': (0, 0, 128, 255), 'ivory2': (238, 238, 224, 255), 'darkmagenta': (139, 0, 139, 255), 'tan': (210, 180, 140, 255), 'gray14': (36, 36, 36, 255), 'goldenrod2': (238, 180, 34, 255), 'grey76': (194, 194, 194, 255), 'gray23': (59, 59, 59, 255), 'skyblue': (135, 206, 235, 255), 'darkgoldenrod4': (139, 101, 8, 255), 'firebrick2': (238, 44, 44, 255), 'darkslategrey': (47, 79, 79, 255), 'grey100': (255, 255, 255, 255), 'grey9': (23, 23, 23, 255), 'pink4': (139, 99, 108, 255), 'slategray4': (108, 123, 139, 255), 'grey69': (176, 176, 176, 255), 'gray5': (13, 13, 13, 255), 'turquoise4': (0, 134, 139, 255), 'mediumorchid3': (180, 82, 205, 255), 'darkslategray3': (121, 205, 205, 255), 'wheat1': (255, 231, 186, 255), 'chocolate3': (205, 102, 29, 255), 'grey25': (64, 64, 64, 255), 'darkslategray4': (82, 139, 139, 255), 'coral3': (205, 91, 69, 255), 'gray94': (240, 240, 240, 255), 'orange3': (205, 133, 0, 255), 'darkseagreen1': (193, 255, 193, 255), 'orangered3': (205, 55, 0, 255), 'grey12': (31, 31, 31, 255), 'gray62': (158, 158, 158, 255), 'grey79': (201, 201, 201, 255), 'lightcoral': (240, 128, 128, 255), 'mistyrose': (255, 228, 225, 255), 'gray75': (191, 191, 191, 255), 'slategray3': (159, 182, 205, 255), 'pink2': (238, 169, 184, 255), 'dimgrey': (105, 105, 105, 255), 'grey10': (26, 26, 26, 255), 'green1': (0, 255, 0, 255), 'grey20': (51, 51, 51, 255), 'dimgray': (105, 105, 105, 255), 'grey24': (61, 61, 61, 255), 'khaki2': (238, 230, 133, 255), 'grey13': (33, 33, 33, 255), 'mediumpurple': (147, 112, 219, 255), 'dodgerblue2': (28, 134, 238, 255), 'gray20': (51, 51, 51, 255), 'grey71': (181, 181, 181, 255), 'darkorange2': (238, 118, 0, 255), 'grey80': (204, 204, 204, 255), 'magenta3': (205, 0, 205, 255), 'lemonchiffon3': (205, 201, 165, 255), 'lightblue1': (191, 239, 255, 255), 'lightgoldenrod4': (139, 129, 76, 255), 'lawngreen': (124, 252, 0, 255), 'grey94': (240, 240, 240, 255), 'olivedrab2': (179, 238, 58, 255), 'gold': (255, 215, 0, 255), 'green': (0, 255, 0, 255), 'navajowhite4': (139, 121, 94, 255), 'grey45': (115, 115, 115, 255), 'mediumorchid': (186, 85, 211, 255), 'lemonchiffon1': (255, 250, 205, 255), 'lightsteelblue3': (162, 181, 205, 255), 'lightyellow2': (238, 238, 209, 255), 'gray45': (115, 115, 115, 255), 'peachpuff': (255, 218, 185, 255), 'peachpuff4': (139, 119, 101, 255), 'blue': (0, 0, 255, 255), 'chartreuse3': (102, 205, 0, 255), 'lightcyan3': (180, 205, 205, 255), 'gray15': (38, 38, 38, 255), 'grey6': (15, 15, 15, 255), 'gainsboro': (220, 220, 220, 255), 'cyan4': (0, 139, 139, 255), 'grey0': (0, 0, 0, 255), 'grey21': (54, 54, 54, 255), 'deeppink3': (205, 16, 118, 255), 'aquamarine4': (69, 139, 116, 255), 'moccasin': (255, 228, 181, 255), 'violetred4': (139, 34, 82, 255), 'grey17': (43, 43, 43, 255), 'red': (255, 0, 0, 255), 'grey53': (135, 135, 135, 255), 'indianred3': (205, 85, 85, 255), 'lightskyblue2': (164, 211, 238, 255), 'gray41': (105, 105, 105, 255), 'slateblue4': (71, 60, 139, 255), 'gold1': (255, 215, 0, 255), 'orangered4': (139, 37, 0, 255), 'yellowgreen': (154, 205, 50, 255), 'grey54': (138, 138, 138, 255), 'brown3': (205, 51, 51, 255), 'slategray1': (198, 226, 255, 255), 'olivedrab4': (105, 139, 34, 255), 'lightgrey': (211, 211, 211, 255), 'gray95': (242, 242, 242, 255), 'hotpink': (255, 105, 180, 255), 'paleturquoise2': (174, 238, 238, 255), 'navajowhite1': (255, 222, 173, 255), 'gray63': (161, 161, 161, 255), 'gray32': (82, 82, 82, 255), 'mintcream': (245, 255, 250, 255), 'yellow': (255, 255, 0, 255), 'gray61': (156, 156, 156, 255), 'slategray': (112, 128, 144, 255), 'gray52': (133, 133, 133, 255), 'lemonchiffon4': (139, 137, 112, 255), 'gray67': (171, 171, 171, 255), 'gray89': (227, 227, 227, 255), 'purple1': (155, 48, 255, 255), 'grey78': (199, 199, 199, 255), 'darkgoldenrod1': (255, 185, 15, 255), 'lightsalmon4': (139, 87, 66, 255), 'gray79': (201, 201, 201, 255), 'grey93': (237, 237, 237, 255), 'ivory3': (205, 205, 193, 255), 'bisque4': (139, 125, 107, 255), 'gray2': (5, 5, 5, 255), 'mediumorchid1': (224, 102, 255, 255), 'goldenrod': (218, 165, 32, 255), 'ghostwhite': (248, 248, 255, 255), 'gray46': (117, 117, 117, 255), 'magenta': (255, 0, 255, 255), 'azure4': (131, 139, 139, 255), 'gray39': (99, 99, 99, 255), 'grey22': (56, 56, 56, 255), 'violetred1': (255, 62, 150, 255), 'darkgoldenrod3': (205, 149, 12, 255), 'lavenderblush3': (205, 193, 197, 255), 'gray88': (224, 224, 224, 255), 'pink3': (205, 145, 158, 255), 'seagreen3': (67, 205, 128, 255), 'deeppink1': (255, 20, 147, 255), 'steelblue4': (54, 100, 139, 255), 'lightsalmon': (255, 160, 122, 255), 'lightcyan': (224, 255, 255, 255), 'chocolate1': (255, 127, 36, 255), 'grey43': (110, 110, 110, 255), 'maroon4': (139, 28, 98, 255), 'gray60': (153, 153, 153, 255), 'darkorchid1': (191, 62, 255, 255), 'indianred1': (255, 106, 106, 255), 'darkseagreen4': (105, 139, 105, 255), 'palevioletred4': (139, 71, 93, 255), 'darkblue': (0, 0, 139, 255), 'cyan': (0, 255, 255, 255), 'paleturquoise3': (150, 205, 205, 255), 'grey49': (125, 125, 125, 255), 'lightskyblue4': (96, 123, 139, 255), 'honeydew3': (193, 205, 193, 255), 'royalblue1': (72, 118, 255, 255), 'indianred2': (238, 99, 99, 255), 'lavenderblush4': (139, 131, 134, 255), 'gray92': (235, 235, 235, 255), 'darkviolet': (148, 0, 211, 255), 'grey85': (217, 217, 217, 255), 'gray87': (222, 222, 222, 255), 'grey55': (140, 140, 140, 255), 'darkorange': (255, 140, 0, 255), 'darkgoldenrod': (184, 134, 11, 255), 'lightskyblue3': (141, 182, 205, 255), 'grey34': (87, 87, 87, 255), 'rosybrown4': (139, 105, 105, 255), 'seagreen4': (46, 139, 87, 255), 'gray53': (135, 135, 135, 255), 'magenta4': (139, 0, 139, 255), 'orange': (255, 165, 0, 255), 'cornsilk3': (205, 200, 177, 255), 'darkorange1': (255, 127, 0, 255), 'red4': (139, 0, 0, 255), 'gray64': (163, 163, 163, 255), 'blue4': (0, 0, 139, 255), 'peachpuff1': (255, 218, 185, 255), 'gray25': (64, 64, 64, 255), 'lavenderblush': (255, 240, 245, 255), 'snow2': (238, 233, 233, 255), 'paleturquoise4': (102, 139, 139, 255), 'gray0': (0, 0, 0, 255), 'darkturquoise': (0, 206, 209, 255), 'orange2': (238, 154, 0, 255), 'blueviolet': (138, 43, 226, 255), 'lightcyan1': (224, 255, 255, 255), 'mediumspringgreen': (0, 250, 154, 255), 'antiquewhite4': (139, 131, 120, 255), 'rosybrown3': (205, 155, 155, 255), 'dodgerblue3': (24, 116, 205, 255), 'snow3': (205, 201, 201, 255), 'gray33': (84, 84, 84, 255), 'lightslateblue': (132, 112, 255, 255), 'gray54': (138, 138, 138, 255), 'navajowhite': (255, 222, 173, 255), 'grey63': (161, 161, 161, 255), 'skyblue1': (135, 206, 255, 255), 'beige': (245, 245, 220, 255), 'grey31': (79, 79, 79, 255), 'magenta1': (255, 0, 255, 255), 'gray24': (61, 61, 61, 255), 'grey67': (171, 171, 171, 255), 'lightsteelblue2': (188, 210, 238, 255), 'darkseagreen': (143, 188, 143, 255), 'mistyrose3': (205, 183, 181, 255), 'gray40': (102, 102, 102, 255), 'violetred': (208, 32, 144, 255), 'purple4': (85, 26, 139, 255), 'grey47': (120, 120, 120, 255), 'purple2': (145, 44, 238, 255), 'tan3': (205, 133, 63, 255), 'mediumseagreen': (60, 179, 113, 255), 'blanchedalmond': (255, 235, 205, 255), 'springgreen2': (0, 238, 118, 255), 'pink1': (255, 181, 197, 255), 'coral2': (238, 106, 80, 255), 'seashell': (255, 245, 238, 255), 'gray59': (150, 150, 150, 255), 'grey66': (168, 168, 168, 255), 'chocolate4': (139, 69, 19, 255), 'lightgray': (211, 211, 211, 255), 'thistle2': (238, 210, 238, 255), 'ivory4': (139, 139, 131, 255), 'cyan2': (0, 238, 238, 255), 'purple': (160, 32, 240, 255), 'grey81': (207, 207, 207, 255), 'orangered2': (238, 64, 0, 255), 'grey15': (38, 38, 38, 255), 'brown': (165, 42, 42, 255), 'gray100': (255, 255, 255, 255), 'grey7': (18, 18, 18, 255), 'grey51': (130, 130, 130, 255), 'palegoldenrod': (238, 232, 170, 255), 'lightsalmon3': (205, 129, 98, 255), 'slateblue1': (131, 111, 255, 255), 'mistyrose2': (238, 213, 210, 255), 'ivory': (255, 255, 240, 255), 'burlywood3': (205, 170, 125, 255), 'lightslategrey': (119, 136, 153, 255), 'grey97': (247, 247, 247, 255), 'orangered': (255, 69, 0, 255), 'lightgoldenrod3': (205, 190, 112, 255), 'darkolivegreen1': (202, 255, 112, 255), 'firebrick': (178, 34, 34, 255), 'hotpink1': (255, 110, 180, 255), 'navy': (0, 0, 128, 255), 'darkolivegreen': (85, 107, 47, 255), 'turquoise2': (0, 229, 238, 255), 'grey92': (235, 235, 235, 255), 'grey16': (41, 41, 41, 255), 'grey26': (66, 66, 66, 255), 'honeydew1': (240, 255, 240, 255), 'aquamarine2': (118, 238, 198, 255), 'dodgerblue4': (16, 78, 139, 255), 'lightgoldenrodyellow': (250, 250, 210, 255), 'blue3': (0, 0, 205, 255), 'azure': (240, 255, 255, 255), 'salmon1': (255, 140, 105, 255), 'blue2': (0, 0, 238, 255), 'lightpink': (255, 182, 193, 255), 'deeppink': (255, 20, 147, 255), 'palegreen4': (84, 139, 84, 255), 'grey91': (232, 232, 232, 255), 'grey18': (46, 46, 46, 255), 'gray81': (207, 207, 207, 255), 'gray7': (18, 18, 18, 255), 'lightsteelblue': (176, 196, 222, 255), 'seagreen2': (78, 238, 148, 255), 'grey73': (186, 186, 186, 255), 'cyan3': (0, 205, 205, 255), 'grey88': (224, 224, 224, 255), 'gray35': (89, 89, 89, 255), 'peachpuff2': (238, 203, 173, 255), 'gray28': (71, 71, 71, 255), 'bisque2': (238, 213, 183, 255), 'orchid': (218, 112, 214, 255), 'grey61': (156, 156, 156, 255), 'grey11': (28, 28, 28, 255), 'mediumaquamarine': (102, 205, 170, 255), 'lightslategray': (119, 136, 153, 255), 'grey87': (222, 222, 222, 255), 'brown1': (255, 64, 64, 255), 'darkorchid2': (178, 58, 238, 255), 'coral1': (255, 114, 86, 255), 'forestgreen': (34, 139, 34, 255), 'darkorchid4': (104, 34, 139, 255), 'lightyellow3': (205, 205, 180, 255), 'violetred2': (238, 58, 140, 255), 'dodgerblue1': (30, 144, 255, 255), 'plum3': (205, 150, 205, 255), 'burlywood4': (139, 115, 85, 255), 'orchid1': (255, 131, 250, 255), 'antiquewhite': (250, 235, 215, 255), 'grey44': (112, 112, 112, 255), 'papayawhip': (255, 239, 213, 255), 'darkseagreen2': (180, 238, 180, 255), 'khaki1': (255, 246, 143, 255), 'gray82': (209, 209, 209, 255), 'olivedrab1': (192, 255, 62, 255), 'magenta2': (238, 0, 238, 255), 'azure3': (193, 205, 205, 255), 'sienna4': (139, 71, 38, 255), 'lightblue4': (104, 131, 139, 255), 'bisque3': (205, 183, 158, 255), 'cornsilk4': (139, 136, 120, 255), 'grey4': (10, 10, 10, 255), 'grey23': (59, 59, 59, 255), 'salmon4': (139, 76, 57, 255), 'cornsilk2': (238, 232, 205, 255), 'grey64': (163, 163, 163, 255), 'darkolivegreen4': (110, 139, 61, 255), 'grey56': (143, 143, 143, 255), 'deepskyblue3': (0, 154, 205, 255), 'wheat2': (238, 216, 174, 255), 'grey14': (36, 36, 36, 255), 'peru': (205, 133, 63, 255), 'brown4': (139, 35, 35, 255), 'lightpink2': (238, 162, 173, 255), 'lemonchiffon': (255, 250, 205, 255), 'gray29': (74, 74, 74, 255), 'cadetblue4': (83, 134, 139, 255), 'gray31': (79, 79, 79, 255), 'darkolivegreen2': (188, 238, 104, 255), 'dodgerblue': (30, 144, 255, 255), 'seagreen': (46, 139, 87, 255), 'honeydew2': (224, 238, 224, 255), 'gray51': (130, 130, 130, 255), 'gray19': (48, 48, 48, 255), 'darkgray': (169, 169, 169, 255), 'orchid2': (238, 122, 233, 255), 'paleturquoise1': (187, 255, 255, 255), 'greenyellow': (173, 255, 47, 255), 'firebrick4': (139, 26, 26, 255), 'darkred': (139, 0, 0, 255), 'antiquewhite3': (205, 192, 176, 255), 'mediumblue': (0, 0, 205, 255), 'salmon': (250, 128, 114, 255), 'gray43': (110, 110, 110, 255), 'lightgoldenrod1': (255, 236, 139, 255), 'wheat3': (205, 186, 150, 255), 'lightblue': (173, 216, 230, 255), 'gray57': (145, 145, 145, 255), 'grey58': (148, 148, 148, 255), 'lightsteelblue4': (110, 123, 139, 255), 'steelblue': (70, 130, 180, 255), 'grey2': (5, 5, 5, 255), 'saddlebrown': (139, 69, 19, 255), 'azure1': (240, 255, 255, 255), 'gray77': (196, 196, 196, 255), 'turquoise1': (0, 245, 255, 255), 'mistyrose4': (139, 125, 123, 255), 'purple3': (125, 38, 205, 255), 'grey39': (99, 99, 99, 255), 'seashell3': (205, 197, 191, 255), 'slategrey': (112, 128, 144, 255), 'paleturquoise': (175, 238, 238, 255), 'olivedrab3': (154, 205, 50, 255), 'grey52': (133, 133, 133, 255), 'royalblue2': (67, 110, 238, 255), 'grey74': (189, 189, 189, 255), 'grey72': (184, 184, 184, 255), 'gray58': (148, 148, 148, 255), 'lightpink4': (139, 95, 101, 255), 'cadetblue': (95, 158, 160, 255), 'grey70': (179, 179, 179, 255), 'mediumorchid4': (122, 55, 139, 255), 'gray90': (229, 229, 229, 255), 'grey29': (74, 74, 74, 255), 'darkorchid3': (154, 50, 205, 255), 'floralwhite': (255, 250, 240, 255), 'lightyellow4': (139, 139, 122, 255), 'grey5': (13, 13, 13, 255), 'violet': (238, 130, 238, 255), 'yellow3': (205, 205, 0, 255), 'sienna3': (205, 104, 57, 255), 'hotpink2': (238, 106, 167, 255), 'gray50': (127, 127, 127, 255), 'lavenderblush2': (238, 224, 229, 255), 'aquamarine': (127, 255, 212, 255), 'hotpink4': (139, 58, 98, 255), 'grey83': (212, 212, 212, 255), 'bisque': (255, 228, 196, 255), 'tomato4': (139, 54, 38, 255), 'mistyrose1': (255, 228, 225, 255), 'gold4': (139, 117, 0, 255), 'goldenrod1': (255, 193, 37, 255), 'goldenrod3': (205, 155, 29, 255), 'navajowhite2': (238, 207, 161, 255), 'gray78': (199, 199, 199, 255), 'red1': (255, 0, 0, 255), 'grey19': (48, 48, 48, 255), 'darkseagreen3': (155, 205, 155, 255), 'honeydew': (240, 255, 240, 255), 'grey89': (227, 227, 227, 255), 'darkorchid': (153, 50, 204, 255), 'gray99': (252, 252, 252, 255), 'slateblue3': (105, 89, 205, 255), 'khaki': (240, 230, 140, 255), 'lightpink3': (205, 140, 149, 255), 'palegreen1': (154, 255, 154, 255), 'grey1': (3, 3, 3, 255), 'gray26': (66, 66, 66, 255), 'olivedrab': (107, 142, 35, 255), 'steelblue2': (92, 172, 238, 255), 'rosybrown2': (238, 180, 180, 255), 'gray18': (46, 46, 46, 255), 'seagreen1': (84, 255, 159, 255), 'tan1': (255, 165, 79, 255), 'gray38': (97, 97, 97, 255), 'darkgrey': (169, 169, 169, 255), 'mediumpurple4': (93, 71, 139, 255), 'orchid4': (139, 71, 137, 255), 'grey40': (102, 102, 102, 255), 'palevioletred3': (205, 104, 137, 255), 'darkorange3': (205, 102, 0, 255), 'gray48': (122, 122, 122, 255), 'coral4': (139, 62, 47, 255), 'grey30': (77, 77, 77, 255), 'cyan1': (0, 255, 255, 255), 'gray42': (107, 107, 107, 255), 'maroon1': (255, 52, 179, 255), 'grey86': (219, 219, 219, 255), 'grey65': (166, 166, 166, 255), 'khaki3': (205, 198, 115, 255), 'darkslategray1': (151, 255, 255, 255), 'palegreen3': (124, 205, 124, 255), 'skyblue2': (126, 192, 238, 255), 'indianred': (205, 92, 92, 255), 'crimson':(220,20,60), 'linen': (250, 240, 230, 255), 'oldlace': (253, 245, 230, 255), 'goldenrod4': (139, 105, 20, 255), 'gray69': (176, 176, 176, 255), 'gray93': (237, 237, 237, 255), 'steelblue1': (99, 184, 255, 255), 'orange4': (139, 90, 0, 255), 'seashell4': (139, 134, 130, 255), 'gray98': (250, 250, 250, 255), 'thistle4': (139, 123, 139, 255), 'darkslategray2': (141, 238, 238, 255), 'grey': (190, 190, 190, 255), 'deeppink4': (139, 10, 80, 255), 'violetred3': (205, 50, 120, 255), 'coral': (255, 127, 80, 255), 'lightyellow': (255, 255, 224, 255), 'tomato1': (255, 99, 71, 255), 'aquamarine3': (102, 205, 170, 255), 'gray97': (247, 247, 247, 255), 'peachpuff3': (205, 175, 149, 255), 'azure2': (224, 238, 238, 255), 'grey33': (84, 84, 84, 255), 'rosybrown1': (255, 193, 193, 255), 'snow1': (255, 250, 250, 255), 'lightskyblue': (135, 206, 250, 255), 'grey38': (97, 97, 97, 255), 'antiquewhite2': (238, 223, 204, 255), 'grey90': (229, 229, 229, 255), 'gold2': (238, 201, 0, 255), 'palegreen': (152, 251, 152, 255), 'salmon3': (205, 112, 84, 255), 'grey77': (196, 196, 196, 255), 'lightcyan4': (122, 139, 139, 255), 'grey59': (150, 150, 150, 255), 'lightgoldenrod': (238, 221, 130, 255), 'red3': (205, 0, 0, 255), 'gray76': (194, 194, 194, 255), 'gray17': (43, 43, 43, 255), 'gray74': (189, 189, 189, 255), 'mediumturquoise': (72, 209, 204, 255), 'mediumorchid2': (209, 95, 238, 255), 'gray85': (217, 217, 217, 255), 'gray71': (181, 181, 181, 255), 'bisque1': (255, 228, 196, 255), 'maroon2': (238, 48, 167, 255), 'gray37': (94, 94, 94, 255), 'gray91': (232, 232, 232, 255), 'royalblue3': (58, 95, 205, 255), 'khaki4': (139, 134, 78, 255), 'gray13': (33, 33, 33, 255), 'sienna1': (255, 130, 71, 255), 'tomato2': (238, 92, 66, 255), 'slategray2': (185, 211, 238, 255), 'navajowhite3': (205, 179, 139, 255), 'tomato': (255, 99, 71, 255), 'turquoise': (64, 224, 208, 255), 'springgreen': (0, 255, 127, 255), 'lightsalmon2': (238, 149, 114, 255), 'lightsalmon1': (255, 160, 122, 255), 'grey60': (153, 153, 153, 255), 'gray34': (87, 87, 87, 255), 'salmon2': (238, 130, 98, 255), 'grey62': (158, 158, 158, 255), 'grey82': (209, 209, 209, 255), 'plum4': (139, 102, 139, 255), 'burlywood': (222, 184, 135, 255), 'gray96': (245, 245, 245, 255), 'chocolate': (210, 105, 30, 255), 'yellow1': (255, 255, 0, 255), 'lightyellow1': (255, 255, 224, 255), 'gray68': (173, 173, 173, 255), 'palevioletred': (219, 112, 147, 255), 'firebrick1': (255, 48, 48, 255), 'plum1': (255, 187, 255, 255), 'springgreen4': (0, 139, 69, 255), 'seashell1': (255, 245, 238, 255), 'indianred4': (139, 58, 58, 255), 'gray1': (3, 3, 3, 255), 'thistle1': (255, 225, 255, 255), 'lightskyblue1': (176, 226, 255, 255), 'lightcyan2': (209, 238, 238, 255), 'mediumvioletred': (199, 21, 133, 255), 'grey95': (242, 242, 242, 255), 'lemonchiffon2': (238, 233, 191, 255), 'cornflowerblue': (100, 149, 237, 255), 'springgreen3': (0, 205, 102, 255), 'lightsteelblue1': (202, 225, 255, 255), 'lavender': (230, 230, 250, 255), 'chartreuse1': (127, 255, 0, 255), 'whitesmoke': (245, 245, 245, 255), 'grey96': (245, 245, 245, 255), 'grey50': (127, 127, 127, 255), 'gray84': (214, 214, 214, 255), 'orange1': (255, 165, 0, 255), 'firebrick3': (205, 38, 38, 255), 'burlywood2': (238, 197, 145, 255), 'snow': (255, 250, 250, 255), 'gray47': (120, 120, 120, 255), 'blue1': (0, 0, 255, 255), 'green2': (0, 238, 0, 255), 'deeppink2': (238, 18, 137, 255), 'gray65': (166, 166, 166, 255), 'gray8': (20, 20, 20, 255), 'gray55': (140, 140, 140, 255), 'gray27': (69, 69, 69, 255), 'seashell2': (238, 229, 222, 255), 'lightgoldenrod2': (238, 220, 130, 255), 'grey98': (250, 250, 250, 255), 'gray11': (28, 28, 28, 255), 'deepskyblue': (0, 191, 255, 255), 'plum2': (238, 174, 238, 255), 'snow4': (139, 137, 137, 255), 'cornsilk': (255, 248, 220, 255), 'darkcyan': (0, 139, 139, 255), 'orangered1': (255, 69, 0, 255), 'lavenderblush1': (255, 240, 245, 255), 'gray': (190, 190, 190, 255), 'darkkhaki': (189, 183, 107, 255), 'grey37': (94, 94, 94, 255), 'black': (0, 0, 0, 255), 'darkolivegreen3': (162, 205, 90, 255), 'darkgreen': (0, 100, 0, 255), 'chocolate2': (238, 118, 33, 255), 'sienna2': (238, 121, 66, 255), 'darkslateblue': (72, 61, 139, 255), 'grey27': (69, 69, 69, 255), 'gray21': (54, 54, 54, 255), 'darkslategray': (47, 79, 79, 255), 'wheat': (245, 222, 179, 255), 'grey3': (8, 8, 8, 255), 'maroon3': (205, 41, 144, 255), 'gray70': (179, 179, 179, 255), 'springgreen1': (0, 255, 127, 255), 'cornsilk1': (255, 248, 220, 255), 'palevioletred2': (238, 121, 159, 255), 'powderblue': (176, 224, 230, 255), 'thistle': (216, 191, 216, 255), 'aliceblue': (240, 248, 255, 255), 'gray12': (31, 31, 31, 255), 'grey36': (92, 92, 92, 255), 'lightpink1': (255, 174, 185, 255), 'ivory1': (255, 255, 240, 255), 'white': (255, 255, 255, 255), 'lightblue3': (154, 192, 205, 255), 'grey42': (107, 107, 107, 255), 'royalblue': (65, 105, 225, 255), 'gray80': (204, 204, 204, 255), 'mediumpurple1': (171, 130, 255, 255), 'gray56': (143, 143, 143, 255), 'gray36': (92, 92, 92, 255), 'lightseagreen': (32, 178, 170, 255), 'gray22': (56, 56, 56, 255), 'cadetblue2': (142, 229, 238, 255), 'mediumpurple2': (159, 121, 238, 255), 'wheat4': (139, 126, 102, 255), 'gray9': (23, 23, 23, 255), 'gray83': (212, 212, 212, 255), 'mediumslateblue': (123, 104, 238, 255), 'gray30': (77, 77, 77, 255), 'darksalmon': (233, 150, 122, 255), 'cadetblue1': (152, 245, 255, 255), 'darkgoldenrod2': (238, 173, 14, 255), 'grey84': (214, 214, 214, 255), 'yellow4': (139, 139, 0, 255), 'chartreuse': (127, 255, 0, 255), 'palegreen2': (144, 238, 144, 255), 'deepskyblue4': (0, 104, 139, 255), 'slateblue': (106, 90, 205, 255), 'thistle3': (205, 181, 205, 255), 'turquoise3': (0, 197, 205, 255), 'sienna': (160, 82, 45, 255), 'deepskyblue1': (0, 191, 255, 255), 'skyblue3': (108, 166, 205, 255), 'grey8': (20, 20, 20, 255), 'red2': (238, 0, 0, 255), 'steelblue3': (79, 148, 205, 255), 'grey48': (122, 122, 122, 255), 'limegreen': (50, 205, 50, 255), 'grey46': (117, 117, 117, 255), 'green4': (0, 139, 0, 255), 'gray44': (112, 112, 112, 255), 'chartreuse2': (118, 238, 0, 255), 'grey68': (173, 173, 173, 255), 'grey35': (89, 89, 89, 255), 'grey41': (105, 105, 105, 255), 'aquamarine1': (127, 255, 212, 255), 'darkorange4': (139, 69, 0, 255), 'grey57': (145, 145, 145, 255), 'gray10': (26, 26, 26, 255), 'tan2': (238, 154, 73, 255), 'chartreuse4': (69, 139, 0, 255), 'antiquewhite1': (255, 239, 219, 255), 'mediumpurple3': (137, 104, 205, 255), 'gray6': (15, 15, 15, 255), 'lightgreen': (144, 238, 144, 255), 'rosybrown': (188, 143, 143, 255), 'tan4': (139, 90, 43, 255), 'gray86': (219, 219, 219, 255), 'brown2': (238, 59, 59, 255), 'grey28': (71, 71, 71, 255), 'palevioletred1': (255, 130, 171, 255), 'grey75': (191, 191, 191, 255), 'hotpink3': (205, 96, 144, 255), 'sandybrown': (244, 164, 96, 255), 'green3': (0, 205, 0, 255), 'gray3': (8, 8, 8, 255), 'midnightblue': (25, 25, 112, 255), 'gray16': (41, 41, 41, 255), 'gray66': (168, 168, 168, 255), 'gray4': (10, 10, 10, 255), 'grey99': (252, 252, 252, 255), 'yellow2': (238, 238, 0, 255), 'maroon': (176, 48, 96, 255), 'burlywood1': (255, 211, 155, 255), 'grey32': (82, 82, 82, 255), 'cadetblue3': (122, 197, 205, 255), 'lightblue2': (178, 223, 238, 255), 'royalblue4': (39, 64, 139, 255), 'gray72': (184, 184, 184, 255), 'gray49': (125, 125, 125, 255), 'gold3': (205, 173, 0, 255), 'honeydew4': (131, 139, 131, 255), 'gray73': (186, 186, 186, 255), 'orchid3': (205, 105, 201, 255), 'pink': (255, 192, 203, 255),'plum': (221, 160, 221, 255), "indigo": (29, 0, 51)}

class PyConsoleGraphicsException(Exception):
    """Base exception for PyConsoleGraphics-specific errors."""

class InputAlreadyActiveError(PyConsoleGraphicsException):
    """When you try to activate an InputCursor but another InputCursor is
    already active, it raises this exception."""

class CursorOverflowError(PyConsoleGraphicsException):
    """Raised by the Cursor when it's asked to do something that would push
    it past the edges of the terminal. This should never be raised itself;
    HorizontalCursorOverflow or VerticleCursorOverflow should be raised
    instead; catching CursorOverflow will catch both."""

class HorizontalCursorOverflowError(CursorOverflowError):
    """Raised by the Cursor when it is asked to do something that would push
    its x position below zero or past the terminal's width, and has been told
    not to deal with the problem itself."""

class VerticalCursorOverflowError(CursorOverflowError):
    """Raised by the Cursor when it is asked to do something that would push
    its y position below zero or past the terminal's height, and has been
    told not to deal with the problem itself."""

class ClickZoneError(PyConsoleGraphicsException):
    """Raised when the ClickZone system detects that it is in some kind of
    invalid configuration."""

class OverlappingZoneError(ClickZoneError):
    """Raised by ClickZone.__init__ when the ClickZone you are specifying
    would overlap with another ClickZone in the same group."""

class DuplicateClickZoneHotkeyError(ClickZoneError):
    """Raised by ClickZone.__init__ when you try to create a ClickZone with a
    hotkey that is already assigned to another ClickZone in the group you're
    putting that ClickZone in, or by ClickZoneManager when you try to
    activate a group that would cause a hotkey collision."""

class ActiveGroupAlterationError(ClickZoneError):
    """Raised when you try to add a ClickZone to an active group."""

class InactiveGroupDeactivationError(ClickZoneError):
    """Raised when you try to deactivate an inactive group."""

class GroupDoesNotExistError(ClickZoneError):
    """Raised when you try to do certain operations, such as activating the
    group, on a group that has never had members added to it and thus does
    not exist."""

class ClickZoneValidationError(ClickZoneError):
    """Subclasses of this are raised by _ClickZoneManager.run_validation
    when an active validation step fails."""

class ClickZoneLinkBidirectionalityError(ClickZoneValidationError):
    """The graph of clickzones, where edges represent where arrow key presses
    move the highlight, is supposed to be undirected. Clickzone validation
    raises this exception if it detects that a clickzone is linked to another
    clickzone but that connection is not mirrored on the other side,
    or in other words when pressing a combination of arrow keys, and then
    pressing the opposite arrow keys in reverse order, would not take you
    back to the place you started."""

class ClickZoneIslandError(ClickZoneValidationError):
    """Raised by _ClickZoneManger.run_validation if it detects that
    activating a group would cause the graph of ClickZone links to no longer
    be strongly connected - in other words, when there are ClickZone-s that
    cannot be accessed with the arrow keys because there's at least one pair
    of clickzones that have no path between each other."""

class Pos(collections.namedtuple("Position", ["x","y"])):
    """Think 'vector' if you know what that means. Represents a location in 2-D
    cartesian space.

    This is a very simple class, basically just a named tuple plus addition and
    subtraction operators that make it easier to offest positions from one
    another."""

    def __new__(cls, x, y=None):
        if y is None:
            x, y = x
        return super().__new__(cls, x, y)

    def __add__(self, other):
        return type(self)(self[0]+other[0], self[1]+other[1])
    def __sub__(self, other):
        return type(self)(self[0]-other[0], self[1]-other[1])
    def __rsub__(self, other):
        return type(self)(other[0]-self[0], other[1]-self[1])
    def __eq__(self, other):
        return self[0] == other[0] and self[1] == other[1]
    def __gt__(self, other):
        return self[0] > other[0] and self[1] > other[1]
    def __lt__(self, other):
        return self[0] < other[0] and self[1] < other[1]
    def __ge__(self, other):
        return self[0] >= other[0] and self[1] >= other[1]
    def __le__(self, other):
        return self[0] <= other[0] and self[1] <= other[1]
    def __neg__(self):
        return type(self)( -self[0], -self[1] )
    def __round__(self, n=None):
        return type(self)( round(self[0], n), round(self[1], n) )

    def __mul__(self, other):
        try:
            x2, y2 = other
        except TypeError:
            return type(self)( self[0] * other, self[1] * other )
        else:
            x1, y1 = self
            return (x1 * x2) + (y1 * y2)

    def __truediv__(self, other):
        try:
            x2, y2 = other
        except TypeError:
            return self * (1 / other)
        else:
            return type(self)( self[0] / x2, self[1] / y2 )

    def __floordiv__(self, other):
        try:
            x2, y2 = other
        except TypeError:
            return self * (1 // other)
        else:
            return type(self)( self[0] // x2, self[1] // y2 )

    def scale(self, other):
        """Multiply x and y by the values in other.

        >>> Pos(5,10).scale(2,4)
        Pos(10,40)
        """
        return type(self)( self[0]*other[0], self[1]*other[1] )

    #@TODO: Rename this to clamped() because it's immutable you dumbass
    #TODO: also call them upper and lower, since max implies it's inclusive and it's not
    def clamp(self, min=(0,0), max=(float("inf"), float("inf"))):
        """Given a box whose top left corner is min and bottom right corner
        is max, return closest point to this pos inside this box. Min defaults
        to (0,0). Careful: clamps to one LESS than the maximum, so it can be
        used to clamp index positions using a Terminal's .size.

        >>> Pos(5, 5).clamp((10, 0), (20, 20))
        Pos(10, 5)
        >>> Pos(-5,-5).clamp(max=(80, 40))
        Pos(0,0)
        >>> Pos(10,10).clamp(max=(10, 10))
        Pos(9, 9)
        """
        minx, miny = min
        maxx, maxy = max
        if minx > maxx or miny > maxy:
            raise ValueError("Negative range from {} to {}. Did you omit max=?".format(min, max))
        x, y = self
        if   x > maxx - 1: x = maxx - 1
        elif x < minx:     x = minx
        if   y > maxy - 1: y = maxy - 1
        elif y < miny:     y = miny
        return type(self)(x, y)

    def normalized(self):
        """Reduce this vector so that it's 1 unit long."""
        return self / self.length()

    def length(self):
        """Taking this vector as a line, return its length. I.e. (a - b).length() is the length between a and b."""
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def rotate(self, theta, radian=False):
        """Rotate the vector by theta degrees (or radians, if radian=True). If you imagine the vector as a pointer on a
        sheet of paper, this is equivalent to just rotating the pointer around its center (or any point on its length)
        that many degrees.

        >>> Pos(1, 0).rotate(90)
        Pos(0, 1)
        >>> Pos(-1, 1).rotate(180)
        Pos(1, -1)
        >>> Pos(999, 999).rotate(45)

        """
        if not radian:
            theta = math.radians(theta)
        x, y = self
        x = x * math.cos(theta) - y * math.sin(theta)
        y = y * math.sin(theta) + y * math.cos(theta)
        return type(self)(x, y)

    @classmethod
    def random(cls, range=None, max=None):
        """Return a random vector.
            If range is omitted or None, returns a random normalized direction vector.
            If range is a 2-tuple of numbers (call them (a,b)), x and y will both be floats in a <= x < y
            If range is a 2-tuple of 2-tuples (or Pos-es), the vector will be within the box specified by them.
            If range is a list or set or range() object, x and y will be taken out of that range.

            You can use max instead of range, which is equivalent to providing a range from 0, (0,0), etc... to max.
            i.e. to find a random point on a Terminal, use Pos.random(max = myterm.size)
        """
        if range is None and max is None:                 #tau = 2*pi :)
            return cls(0, 1).rotate(random.random() * math.tau, radian=True)

        if hasattr(range, "__getitem__"):
            return cls( random.sample(range, 2) )

        if range is None:
            try:
                maxx, maxy = max
            except TypeError:
                maxx = maxy = range
            range = ((0,0), (maxx, maxy))

        min, max = range
        if hasattr(min[0], "__getitem__"):
            minx, miny = min
            maxx, maxy = max
        else:
            minx = miny = min
            maxx = maxy = max

        x = random.uniform(minx, maxx)
        y = random.uniform(miny, maxy)
        return cls(x, y)

    direction_symbol_map = {(0, 0): "∙", (0, -1): "↑", (0, 1): "↓", (1, 0): "→", (-1, 0): "←",
     (1, 1): "↘", (-1, 1): "↙", (-1, -1): "↖", (1, -1): "↗"}
    def to_character(self):
        """Return a Unicode arrow representing the direction of this vector to within 45 degrees (there's only eight
        arrow characters, plus a centered dot representing (0,0). This assumes (0,0) is the upper left corner, which
        is the convention Pyconsolegraphics uses."""
        normself = self.normalized()
        mydirection = next(sorted(self.direction_symbol_map, key=normself.__mul__, reverse=True))
        return self.direction_symbol_map[mydirection]

    def __hash__(self):
        return hash((self.x, self.y))

class Cursor:
    """A cursor on the terminal screen. A terminal supports an arbitrary
    number of cursors. Cursors have position and write characters in the cells
    under them, moving left (and wrapping around to the next line when they
    run out of left) as they do.

    pos is a 2-tuple representing the initial position of the cursor.

    fgcolor and bgcolor are the foreground and background color respectively of
    text printed with this cursor. A color of "None" represents "whatever
    color is set globally on the Terminal," so text printed with a cursor
    who'se .fgcolor is None will change color when the terminal's .fgcolor
    changes.

    italic, bold, and underline default to False and make characters this
    cursor writes italic, bold, or underlined respectively. Unlike f/bgcolor
    and such these can only be True or False and not None, there is no Terminal-
    wide italic/bold/underline setting.

    If cursorchar is None, the cursor is invisible. If cursorchar is an empty
    string, the cursor does not override the character under it but does still
    draw the bgcolor under the character that is there.

    If .autoscroll is True (which it is by default) the cursor will
    automatically have the terminal scroll down when the cursor moves on from
    the last column of the last row. If .autoscroll is False the cursor will
    just stay where it is in that case.

    The Cursor's initializer automatically adds it to the terminal's
    .cursors list. Make sure to delete it from this list when you don't need
    it anymore."""

    def __init__(self, terminal, pos=(0, 0), fgcolor=None, bgcolor=None,
                 italic=False, bold=False, underline=False, cursorchar='▏',
                 cursorcolorinverse=False, autoscroll=True,
                 blink=True, blinkrate=0.5, allow_wrap=True):
        self.terminal = terminal
        terminal.cursors.append(self)
        self.x, self.y = pos

        self.fgcolor = _color_name_conversion(fgcolor)
        self.bgcolor = _color_name_conversion(bgcolor)
        self.italic = italic
        self.bold = bold
        self.underline = underline

        self.cursorcolorinverse = cursorcolorinverse
        self.autoscroll = autoscroll
        self.allow_wrap = allow_wrap
        self.blink = blink
        self.blinkrate = blinkrate
        self.cursorchar = cursorchar

        self.lastblink = None
        self.currently_blinked = False

        #This is acquired during any modification to the terminal's state;
        #drawing will block until it's not held by anyone.
        self.semaphore = threading.Semaphore(0)

    def __setattr__(self, key, value):
        if key == "x" and not 0 <= value < self.terminal.width:
            raise HorizontalCursorOverflowError("Cursor forced out of bounds: x = {}".format(value))
        if key == "y" and not 0 <= value < self.terminal.height:
            raise VerticalCursorOverflowError("Cursor forced out of bounds: y = {}".format(value))

        super().__setattr__(key, value)

    @property
    def pos(self):
        """Represents the tuple of (self.x, self.y), both for getting and
        setting."""
        return self.x, self.y
    @pos.setter
    def pos(self, newpos):
        self.x, self.y = newpos

    @property
    def fgcolor(self):
        """Foreground color of text written with this cursor. If set to a
        color name, will be converted to a tuple representing that color."""
        return self._fgcolor
    @fgcolor.setter
    def fgcolor(self,newfgcolor):
        self._fgcolor = _color_name_conversion(newfgcolor)

    @property
    def bgcolor(self):
        """Background color of cells written on with this cursor. If set to a
        color name, will be converted to a tuple representing that color."""
        return self._bgcolor
    @bgcolor.setter
    def bgcolor(self,newbgcolor):
        self._bgcolor = _color_name_conversion(newbgcolor)

    def advance(self, steps=1):
        """Move the cursor right as if it just printed a character, honoring the cursor's wrapping settings. May
        scroll the terminal or raise HorizontalCursorOverflowError or VerticalCursorOverflowError depending on the
        cursor's settings."""
        #TODO: This mostly works with negative step values... needs to handle going off the top if I want to make
        # that official.
        unaltered_x = self.x
        if self.allow_wrap:
            self.x = (self.x + steps) % self.terminal.width
            try:
                self.y += (unaltered_x + steps) // self.terminal.width
            except VerticalCursorOverflowError as e:
                for t in range((unaltered_x + steps) // self.terminal.width):
                    if self.autoscroll:
                        self.terminal.scroll_down()
                    else:
                        e.args = (
                            "Advancing {} places puts cursor off bottom of terminal,"
                            " and autoscroll is False",
                        )
                        raise
                #TODO: If I make all Cursors move themselves when the Terminal scrolls, this will have to move itself
                # back down to the bottom
        else:
            if (self.x + steps) >= self.terminal.width:
                raise HorizontalCursorOverflowError(
                        "Advancing {} places puts cursor off right side of "
                        "terminal, and allow_wrap is False"
                    )
            else:
                self.x += steps


    def writechar_raw(self, character):
        """Write the given character at this cursor's position and move to
        the next cell.

        This is a 'raw' way of putting characters at the cursor's position;
        smart_writechar also does things like going down to the next line
        when it sees a newline character.

        By default, if printing the character would cause the cursor to go off
        the right side of the terminal, the cursor will 'wrap' to the beginning
        of the next row; if it sees it will 'wrap' off of the bottom of the
        terminal, it will call .scroll_down() on the terminal first.

        If .autoscroll is not True, the cursor will raise
        VerticalCursorOverflow upon reaching the end of the last line. If
        .wrapping_allowed is not true, the cursor will raise
        HorizontalCursorOverflow upon reaching the end of a line.
        """
        cell = self.terminal[self.x, self.y]
        cell.character = character
        cell.fgcolor = self.fgcolor
        cell.bgcolor = self.bgcolor
        cell.italic = self.italic
        cell.underline = self.underline
        cell.bold = self.bold

        try:
            self.advance()
        except HorizontalCursorOverflowError as e:
            e.args = ("Printing '{0}' put cursor out of bounds "
            "horizontally (character printed but cursor has not moved.)"
            .format(character),)
            raise
        except VerticalCursorOverflowError as e:
            e.args = ("Printing '{0}' put cursor out of bounds "
                      "vertically (character printed but cursor has not moved.)"
                      .format(character),)
            raise

    def process_control_character(self, character):
        r"""If character is a control character, handle it; otherwise raise
        ValueError. Code points < 0x1F (31) and 0x7f (127) are considered
        control characters, control characters other than the ones listed
        here are silently ignored and not printed.

        This is meant to be called from smart_writechar, but you can call it
        yourself if you see a reason to.

        Non-ASCII control characters such as U+200F RIGHT-TO-LEFT MARK are not
        yet supported and will be printed with the U+FFFD REPLACEMENT CHARACTER
        glyph.

        Valid control characters:
        esc. code  Hex  Decimal

        \n         0xC  10      Line feed

        Scrolls the terminal down one line. Note that Python turns CRLFs into
        \n-s automatically when reading from file-like objects or decoding
        byte strings; you _should_ be able to rely on it transparently
        converting the various newline denotations into \n-s for you.

        The terminal does not respect 0xD (carriage return) codes and silently
        ignores them like any other code < 0x1F that it does not know how to
        process.

        \t        0x9  9        Horizontal tab

        Equivalent to printing 4 spaces, unless the cursor is less than 4 spaces
        away from the end of the row, in which case we print spaces up till the
        end of the row and then move down to the next row.

        In other words, move four spaces right, or to the next line if that's
        not possible.


        Input cursors treat these next two characters differently; please see
        the docstring for InputCursor.process_control_character for more
        information.

        \x08       0x8  8       Backspace

        Replace the character at the current cursor position with a space, and
        move the cursor one space to the left.

        \x7F      0x7F  177     Delete

        Replace the character one space to the left of the current cursor
        position with a space.
        """
        # Note the r before this docstring, which among other things disables
        # the \ escape codes

        if ord(character) > 31 and character != "\x7F":
            raise ValueError("Non-control character {0} (code point > 31) "
                             "passed to process_control_character.".format(
                character))

        if character == "\n":
            self._newline()

        elif character == "\x08":
            self._backspace()

        elif character == "\x7F":
            self._delete()

        elif character == "\t":
            spaces = min(4, self.terminal.width - self.y)
            for t in range(spaces): self.writechar_raw(" ")

    def _backspace(self):
        """"Called by process_control_character to handle backspaces."""
        self.x -= 1
        if self.x < 0:
            self.y -= 1
            self.x = self.terminal.width - 1
            if self.y < 0:
                self.x = 0
                self.y = 0

        self.terminal[self.x, self.y].character = " "

    def _newline(self):
        """Called by process_control_character to handle newlines."""
        if self.y < self.terminal.height - 1:
            self.y += 1
            self.x = 0
        else:
            if self.autoscroll:
                self.terminal.scroll_down()
            self.x = 0

    def _delete(self):
        """Called by process_control_character to handle the DELETE
        character."""
        try:
            self.terminal[self.x, self.y].character = " "
        except IndexError:
            pass

    def smart_writechar(self, character):
        """Write the given character at this cursor's position and move to
        the next cell unless it's a special character that must be handled
        differently, like backspace and carriage return.

        Depending on how this Cursor is configured, this may fail and raise
        CursorOverflowError-s; see the documentation for writechar_raw()."""
        try:
            # self.control_char_dispatch[character](self)
            self.process_control_character(character)
        except ValueError:
            self.writechar_raw(character)

    def pre_draw(self):
        """Called by the Terminal right before the backend draws it,
        every time its .draw() is called."""

        if self.blink:
            # The blink timer is based on the system monotonic clock
            # the monotonic goes up by 1 every 1 second, so
            # time.monotonic() - value_from_last_time_you_blinked >
            # blink_every_this_many_seconds will evaluate True every
            # that many seconds.
            if self.lastblink is None:
                # If we haven't set up the blink timer, do so.
                self.lastblink = time.monotonic()
            elif time.monotonic() - self.lastblink >= self.blinkrate:
                self.currently_blinked = not self.currently_blinked
                self.lastblink = time.monotonic()

    def should_draw(self):
        """Called by the backend; return True if the backend should actually
        draw this cursor instead of whatever it's over."""

        # if self.currently_blinked: return False
        # if self.cursorchar is None: return False
        # return True

        # Equivalent to the above
        return not (self.currently_blinked or self.cursorchar is None)

class InputCursor(Cursor):
    """Cursor that can take in text from the keyboard. If .echo is True this
    also writes inputted text to the console at its position just like a
    normal cursor with writechar.

    If input_line_mode is True, the user can't navigate the cursor around the
    screen freely; it can only move as far left (including backspaces) as it
    has right. In other words it means that you can't go and delete text
    that's already there when the program has called input(), you can only
    backspace the text you just entered."""

    def __init__(self, *args, echo=True, input_line_mode=True, **kwargs):
        self.echo = echo
        super().__init__(*args, **kwargs)
        self.buffer = []
        self.bufferposition = 0
        self.input_line_mode = input_line_mode
        self.currently_getting_line = False
        self.return_pressed = True
        self.autodraw_active = False
        # Gets incremented whenever we delete a character so we know later to
        # go back and clear any "dangling" characters from the end of the line
        self.cleanupcount = 0
        self.start_pos = None

    @property
    def currently_active(self):
        """Whether the active input cursor is this cursor. Not
        settable; use activate() and finish() instead."""
        return self.terminal.active_input_cursor == self

    def activate(self):
        """Make this InputCursor the active InputCursor and begin receiving
        keypresses. Will raise InputAlreadyActiveError if another InputCursor
        is already active; wait for it to be done."""
        if self.terminal.active_input_cursor:
            raise InputAlreadyActiveError("There is already an InputCursor "
                                          "listening for keypresses on that "
                                          "terminal.")

        self.terminal.active_input_cursor = self
        self.start_pos = (self.x, self.y)
        self.buffer = []
        self.bufferposition = 0
        self.terminal.hooks.register(self.on_scroll)

    def writechar_raw(self, character):
        super().writechar_raw(character)
        if self.currently_active:
            self.buffer.insert(self.bufferposition, character)
            self.bufferposition += 1

    def _process_chars(self, characters):
        """Only meant to be called by the Terminal this InputCursor is part
        of. Get characters from the backend and add them to the buffer,
        doing whatever extra processing (i.e. printing them if .echo is true) is
        called for."""

        for thecharacter in characters:
            try:
                self.process_control_character(thecharacter)
            except ValueError:
                if self.echo:
                    self.smart_writechar(thecharacter)

    def _process_keys(self, keys):
        for thekey in keys:
            if thekey.key == "left":
                self.bufferposition -= 1
                if self.bufferposition < 0:
                    self.bufferposition = 0
                else:
                    self.x -= 1

            elif thekey.key == "right":
                self.bufferposition += 1
                if self.bufferposition > len(self.buffer):
                    self.bufferposition = len(self.buffer)
                else:
                    self.x += 1

    def _backspace(self):
        # If the buffer is empty and we're in "don't backspace the whole
        # screen" mode, abort
        if self.input_line_mode and not self.buffer:
            self.terminal[self.x, self.y].character = " "
            return

        del self.buffer[self.bufferposition - 1]
        self.bufferposition -= 1
        # There'll be a floating character at the end of the line, so remember
        # to write a space over it
        self.cleanupcount += 1
        super()._backspace()

    def _newline(self):
        if self.currently_getting_line:
            self.return_pressed = True
        if self.currently_active: self.buffer.append("\n")
        super()._newline()

    def finish(self):
        """Deactivate this InputCursor, allowing other InputCursor-s to
        become active, and return the contents of its buffer as a string.
        You'll want to check the .buffer for '\r' to detect the user pressing
        return; the InputCursor just treats it like any other character."""

        self.terminal.active_input_cursor = None
        self.terminal.hooks.unregister(self.on_scroll)
        return "".join(self.buffer)

    def get_line(self, fps=30):
        """Allow the user to type a line of text, returning the text
        currently there when the user presses enter. This is used instead of
        the activate() ... finish() stuff, use this if you just want to
        synchronously get a line of text, allowing the user to type it in
        wherever this InputCursor currently is and finishing and returning
        the string when the user presses Enter.

        Update_rate is the number of times per second this function should
        call its terminal's .draw()."""

        self.currently_getting_line = True
        self.return_pressed = False

        self.activate()

        while not self.return_pressed:
            self.terminal.process()
            self.terminal.draw()
            time.sleep(1 / fps)

        return self.finish()

    def on_scroll(self, scrollvec):
        if not self.currently_active:
            print("on_scroll while inactive", file=sys.__stdout__)
            return #No idea why we're getting on_scroll when we're not actives
        self.start_pos -= scrollvec

    def pre_draw(self):
        if self.currently_active:
            #If you try to input more than a full screen of text, start_pos
            #will be off the top of the screen.
            #TODO: test this with newlines in the buffer
            bufferoffset = 0
            if self.start_pos[1] < 0:
                effective_start_pos = (self.start_pos[0],0)
                linestogo = -self.start_pos[1]
                for n, thechar in enumerate(self.buffer):
                    if thechar == "\n":
                        linestogo -= 1
                    elif n % self.terminal.width == 0 and n != 0:
                        linestogo -= 1
                    if linestogo == 0:
                        bufferoffset = n
                        break
            else:
                effective_start_pos = self.start_pos

            reprintcursor = Cursor(self.terminal, effective_start_pos,
                                   self.fgcolor, self.bgcolor, autoscroll=False)
            for thechar in self.buffer[bufferoffset:]: #this copies the list; may be too slow
                try:
                    reprintcursor.smart_writechar(thechar)
                except CursorOverflowError:
                    break

            #If the user deleted characters in the middle, there will be characters off the
            #end of the input line we need to get rid of.
            for t in range(self.cleanupcount):
                try:
                    reprintcursor.smart_writechar(" ")
                except CursorOverflowError:
                    break
            self.cleanupcount = 0

            self.terminal.cursors.remove(reprintcursor)

        super().pre_draw()


class _ClickZoneManager:
    """An object that holds global information about a single Terminal's
    clickzones. This does things that require information about or apply
    to all clickzones at once, like autogenerating and checking the arrow
    key links, and keeping track of which zone is currently highlighted.

    There can be multiple groups of clickzones; when constructing the
    ClickZone you can specify which group it's in (it's in the "default" group
    if you don't specify) and then control which groups are currently active
    via methods of the ClickZoneManager. Multiple groups can be active at once
    so long as they don't have any overlapping ClickZone-s.

    No group is active by default, including the default group; validation
    is run on groups when they are active. Errors detected in a set of
    ClickZone-s, such as non-bidirectional arrow key links, will be raised as
    ClickZoneError-s from .activate_group().

    ClickZones are allowed to link to other zones in inactive groups,
    but trying to highlight a zone in an inactive group will silently fail
    and leave the currently highlighted zone highlighted.

    There is little cost to calling activate_group() on an already active
    group (validation does not re-run unless you deactivate_group() it first) so
    if you are worried about that silent failure, consider just calling
    activate_group() on the group that contains the target before trying to
    highlight it.

    Only one ClickZone may be highlighted. The highlighted ClickZone is the
    only one that gets its event methods called and is the one whose
    on_activate is called when the user presses enter. A ClickZone can be
    highlighted with the keyboard keys or by the user moving the mouse
    cursor over it.

    Every group must have a default highlighted clickzone; by default it will
    be the first zone added to that group. When the group the currently
    selected clickzone is in is deactivated, or .currently_highlighted becomes
    None for any other reason, the default clickzone of an arbitrarily
    selected currently active group will become highlighted. Consider
    highlighting a zone that makes sense yourself before deactivating the
    group that contains the highlighted zone.

    You can not add ClickZone-s to a currently active group; de-activate it
    first, then re-activate it if you wish after you're done adding new zones.
    """

    def __init__(self, terminal):
        self.terminal=terminal #type: Terminal

        self.currently_highlighted=None #type: ClickZone
        self.zonemap = dict() #type: dict[tuple(int,int), ClickZone]

        self.groups = collections.defaultdict(list) #type: dict[string,list[ClickZone]]
        self.activegroups = dict() #type: dict[string,list[ClickZone]]
        self.hotkeymap = dict() #type: dict[string, ClickZone]

        self.autofill_directional_links = True
        #This isn't on by default because in many cases you actually do want
        # some ClickZone links to not be bidirectional
        self.validate_directional_link_bidirectionality = False

    def draw(self):
        """Call on_draw() on all active ClickZone-s."""
        for thegroup in self.activegroups.values():
            for thezone in thegroup:
                thezone.on_draw((thezone is self.currently_highlighted))

    def clickzone_is_active(self, thezone):
        """Given a ClickZone, return True if it is in an active group managed by
        this ClickzoneManager. This is somewhat slow, so use it sparingly."""
        for thegroup in self.activegroups.values():
            if thezone in thegroup:
                return True
        else:
            return False

    def any_groups_active(self):
        """Return true if any groups are active in this ClickZoneManager at
        all."""
        return bool(self.activegroups)

    def add_clickzone(self, clickzone, group):
        """Add a clickzone to a group. Doesn't actually show it on screen or
        make it available to be clicked on; you have to add it to a group and
        then activate that group.

        Trying to add a clickzone to a group that is currently active will raise
        ActiveGroupAlterationError. Deactivate it first, then re-activate it after
        you're done adding stuff.
        """
        if group in self.activegroups:
           raise ActiveGroupAlterationError("Group {0} is currently active and "
                                       "cannot be added to. Deactivate {0} "
                                       "before adding to it, then reactivate "
                                       "it once you're done so that it can be "
                                       "validated.".format(group))
        self.groups[group].append(clickzone)

    #@TODO: This is incredibly inelegant; unfuck it at some point
    def remove_clickzone(self, clickzone, group="default"):
        """Remove a clickzone from a group. Clickzones can only be in one
        group in the first place; the group parameter is just if you happen
        to already know what group it's in so we don't have to go looking for it.
        You can even be wrong about which group it's in; it'll still work.

        You cannot remove a clickzone that is in an active group;
        ActiveGroupAlterationError will be raised if you try."""
        if clickzone in self.groups[group]:
            if group in self.activegroups:
                raise ActiveGroupAlterationError("Group {0} is currently "
                                                 "active and cannot be "
                                                 "removed from. Deactivate {0}"
                                                 " before removing from it, "
                                                 "then reactivate it once you're"
                                                 "done so that it can be "
                                                 "validated.".format(group))
            self.groups[group].remove(clickzone)

        for thegroup in self.groups.values():
            if clickzone in thegroup:
                if thegroup in self.activegroups:
                    raise ActiveGroupAlterationError("Group {0} is currently "
                                                     "active and cannot be "
                                                     "removed from. "
                                                     "Deactivate "
                                                     "{0} before removing from "
                                                     "it, "
                                                     "then reactivate it once "
                                                     "you're"
                                                     "done so that it can be "
                                                     "validated.".format(thegroup))
                self.groups[group].remove(clickzone)
                return

    def highlight(self, clickzone):
        """Make the given clickzone the currently highlighted clickzone -
        *if* it is in an active group. If it isn't, do nothing."""
        if clickzone is not self.currently_highlighted and self.clickzone_is_active(clickzone):
            if self.currently_highlighted:
                self.currently_highlighted.on_lose_highlight()
            self.currently_highlighted=clickzone
            clickzone.on_highlight()

    link_to_opposite = {"linkup" : "linkdown", "linkleft":"linkright",
                        "linkdown": "linkup", "linkright":"linkleft"}
    link_to_direction = {"linkup" : (0,-1), "linkleft": (-1, 0),
                        "linkdown": (0, 1), "linkright": (1, 0)}
    link_to_func = {"linkup": "on_up_pressed", "linkleft": "on_left_pressed",
                "linkdown": "on_down_pressed", "linkright": "on_right_pressed"}

    def _should_generate_link(self, thezone, link):
        """Given a zone and a link direction attribute (
        linkup/down/left/right), return False if the behavior when that arrow
        key has been pressed has already been specified by the user, or True
        if we should auto-generate a link from that zone in that direction. """
        #if autolinkup/down/left/right is True, the user has told us
        # explicitly to autolink
        if getattr(thezone, "auto" + link, False):
            return True

        #If a link is already specified, we definitely shouldn't autolink
        if getattr(thezone, link, False): return False

        #And if on____press has been overridden, we assume that we shouldn't
        #autolink in that case either (if the user wanted to extend and not
        # override the on____press behavior, he would've set autolink____)
        func = self.link_to_func[link]
        if getattr(thezone, func).__func__ \
                is not getattr(ClickZone,func): return False


        return True

    def find_set(self, zone):
        """Return the set of all ClickZone-s that have links (directly or
        indirectly) to this ClickZone."""
        retset = set()
        stack = [] #type: list[ClickZone]
        stack.append(zone)
        while stack:
            thezone = stack.pop()
            retset.add(thezone)
            if thezone.linkup and thezone.linkup not in retset:
                stack.append(thezone.linkup)
            if thezone.linkleft and thezone.linkleft not in retset:
                stack.append(thezone.linkleft)
            if thezone.linkright and thezone.linkright not in retset:
                stack.append(thezone.linkright)
            if thezone.linkdown and thezone.linkdown not in retset:
                stack.append(thezone.linkdown)
        return retset

    def generate_links(self, group, allow_unidirectional_links=True):
        """For all ClickZone-s in the given group that have
        .linkup/down/left/right parameters that are None, and do not override
        .on_up/down/left/right_pressed, or whiose autolink_up/left/down/right is True,
         automatically fill in enough of those values to make it so each
         ClickZone is reachable with the arrow keys.

         We do this by building a minimum spanning tree from the
         fully-connected graph of ClickZones, where the weight of an edge is
         based on how conformant to the link direction the line between them is,
         and how far apart they are.

         There _is_ a small chance that this process will result in a
         clickzone graph that is not strongly-connected; one that has
         "islands" that you can't get from one to the other. This shouldn't
         happen unless your layout is really weird though. If it does fix it
         by manually specifying links for the zones that are having trouble.

         If allow_unidirectional_links is True - which it is by default -
         this will add redundant links that it thinks make sense in
         addition to the minimum spanning tree; i.e. in this situation:

         1

         2   3

        If allow_unidirectional_links is False, 1.linkdown will be 2,
        2.linkright will be 3, 3.linkleft will be 2 and 2.linkup will be 1.

        If allow_unidrecional_links is True, 1.linkright will also be 3,
        but everything else will be the same; the link from 1 to 3 is
        unidirectional.
         """

        zones = self.groups[group]

        #dot = dot product (google it), dist = euclidian distance
        #tl;dr dot product = how similar two direction vectors are;
        #dot(↑, ↑) = 1, dot(↑, ↗) = 0.5, dot(↑, →) = 0, dot(↑, ↘) = -0.5 ...
        #You can also think of it as how far following the line described by
        #vector A will take you along the line described by vector B.
        dot = lambda a, b: a[0] * b[0] + a[1] * b[1]
        dist = lambda a, b: math.sqrt( (a[0] - b[0]) ** 2 + (a[1] - b[1])**2 )
        sub = lambda a, b: (a[0] - b[0], a[1] - b[1])
        def linkscore(a, b, desireddirection):
            origin=a.center
            destination=b.center
            distance = dist(origin, destination)
            direction = sub(destination, origin)
            direction = direction[0] / distance, direction[1]/distance
            directioncorrectness = dot(direction, desireddirection)
            return (5 * directioncorrectness) / math.log1p(distance)

        try:
            links = [(linkscore(a, b, direction), link, a, b)
                     for a, b in itertools.combinations(zones, 2)
                     for link, direction in self.link_to_direction.items()
                     if
                        self._should_generate_link(a,link) and
                        self._should_generate_link(b,self.link_to_opposite[link])]
        except ZeroDivisionError:
            #Some jackass put two ClickZone-s on top of each other and made
            # our distance calculations come out to zero...no point in
            # continuing, just let the final activation step catch it
            return
        #Let's not even bother sorting links whose score is less than 0
        links.sort(key=lambda x: x[0], reverse=True)
        links = [x for x in links if x[0] > 0]

        #We use Kruskal's MST algorithm to ensure that every ClickZone
        #gets linked to and because it gives more appropriate results; try
        # dummying out the cycle detection check if you don't believe me :P
        trylater=[]
        for score, link, a, b in links:
            opplink = self.link_to_opposite[link]
            #If both a and b are open to be linked this way...
            if not (getattr(a, link) or getattr(b, opplink)):
                if self.find_set(a) == self.find_set(b):
                    trylater.append((a, b, link, opplink))
                    continue
                setattr(a, link, b)
                setattr(b, opplink, a)

        #But if a cycle-causing link didn't get replaced by a non cycle-causing
        #link, we ought to add it too (and they'll already be sorted in
        # descending-score order)
        if allow_unidirectional_links:
            for a, b, link, opplink in trylater:
                if not getattr(a, link):
                    setattr(a, link, b)
                #it may just not have been part of the MST, and we actually
                #can make it bidirectional
                if not getattr(b, opplink):
                    setattr(b, opplink, a)


    def run_validation(self, group):
        """Run all validations on the given group and raise ClickZoneError-s
        to indicate failures to validate. (Except it doesn't yet because this
        will be pretty much the last thing I implement.)

        The "check if ClickZone-s don't overlap" check isn't run here; it's
        done while the zonemap is being built/ammended."""
        #@TODO: Implement ClickZone validation

        zones = self.groups[group]

        if self.validate_directional_link_bidirectionality:
            for thezone in zones:
                for thelink, theopposite in self.link_to_opposite.items():
                    linkage = getattr(thezone, thelink, None)
                    if linkage:
                        reverselinkage = getattr(linkage, theopposite, None)
                        if reverselinkage != thezone:
                            raise ClickZoneLinkBidirectionalityError(
                                """{0}.{1} is {2}, but {2}.{3} is {4}.""".format(
                                    thezone, thelink, linkage,
                                    theopposite, reverselinkage))

        return

    def activate_group(self, group):
        """Given the name of a clickzone group, activate that group, causing
        all the ClickZone-s in it to start receiving on_draw(),
        on_highlight(), and on_click() events. Trying to activate an
        already-active group does nothing."""

        if group in self.activegroups:
            #No point in activating an active group...
            return

        if group not in self.groups:
            raise GroupDoesNotExistError("There is no group by the name of {0}.".format(group))

        if self.autofill_directional_links:
            self.generate_links(group)

        self.run_validation(group)

        self.activegroups[group]=self.groups[group]

        for theclickzone in self.groups[group]:
            if theclickzone.hotkey:
                if theclickzone.hotkey in self.hotkeymap:
                    raise DuplicateClickZoneHotkeyError(
                        "Activating {0} will cause a hotkey collision; {1} stands for both {2} and {3}"
                            .format(group, theclickzone.hotkey,theclickzone,self.hotkeymap[theclickzone.hotkey]))
                else:
                    self.hotkeymap[theclickzone.hotkey]=theclickzone

            centerx, centery = theclickzone.center
            halfwidth = theclickzone.width / 2
            halfheight = theclickzone.height / 2
            #This may break the "biases towards the top-left" promise: look
            # in to that; I had to do it this way to make the way we draw
            # rectangles in .ui match up, but maybe I did something wrong
            # over there...
            dxs = [dx for dx in range(-math.floor(halfwidth), math.ceil(halfwidth))]
            dys = [dy for dy in range(-math.floor(halfheight), math.ceil(halfheight))]
            if not dxs: dxs = [0]
            if not dys: dys = [0]
            cellposes = ((centerx + dx, centery + dy) for dx in dxs for dy in dys)
            for thecellpos in cellposes:
                if thecellpos in self.zonemap:
                    raise OverlappingZoneError("{0} overlaps with {1} at {2}"
                                               .format(theclickzone,
                                                       self.zonemap[thecellpos],
                                                       thecellpos))
                else:
                    self.zonemap[thecellpos]=theclickzone

            theclickzone.on_activate()

    def deactivate_group(self, group, blank_occupied_cells=True):
        """Given the name of a clickzone group, deactivate that group.
        Trying to deactivate a group that isn't active raises
        InactiveGroupDeactivationError().

        if blank_occupied_cells is True (which it is by default) this
        will also blank the cells that were occupied by ClickZone-s in
        this group. if blank_occupied_cells is 'fgonly' only the fgcolor
        and character will be cleared."""
        if group not in self.activegroups:
            raise InactiveGroupDeactivationError("{0} is already inactive."
                                                 .format(group))

        zones = set(self.activegroups[group])
        for pos, thezone in list(self.zonemap.items()):
            if thezone in zones:
                del self.zonemap[pos]

                if blank_occupied_cells:
                    self.terminal[pos].character=None
                    self.terminal[pos].fgcolor=None
                    if blank_occupied_cells != "fgonly":
                        self.terminal[pos].bgcolor=None

        for thehotkey, thezone in list(self.hotkeymap.items()):
            if thezone in zones:
                del self.hotkeymap[thehotkey]

        for thezone in zones:
            thezone.on_deactivate()

        del self.activegroups[group]

class ClickZone: #@TODO: Fill in what exception class a clickzone island will  raise
    """A rectangle of cells on the Terminal that acts as a target for user
    interaction. Can be clicked on with the mouse, as the name suggests,
    but users can also navigate around click zones with the keyboard or
    use hotkeys.

    pos is a Pos object that represents what cell the ClickZone is centered on.
    If the ClickZone's dimensions are even the center will be biased towards the
    top left; i.e. a 2x2 ClickZone at (1,1) will have its top left corner at
    (0,0) and its bottom right corner at (1,1).

    You can manually specify hotkeys and where arrow keys take you from
    a given button, or let PCG automatically generate those at runtime based
    on the labels.

    ClickZone-s may not overlap, unless all but one overlapping ClickZone is
    in an inactive group. The overlap check is run when the ClickZone is
    constructed and the other checks are run on a zone group when that group is
    activated.

    The ClickZoneManager checks for bi-directionality of arrow key links
    and for isolated "islands" of clickzones that mean the user can't reach
    some with the arrow keys; it will raise [...?]Error to alert
    you of this. You can turn these checks off or downgrade them to warnings
    via attributes on the ClickZoneManager (which is held in
    yourterminal.clickzonemanager.)

    This base ClickZone class provides no graphical representation; either draw
    your own UI and use ClickZones to make it actually work, or (and this is
    probably the better way) use the derived classes in pyconsolegraphics.ui.
    """

    def __init__(self, terminal, center, width = 4, height=1, group="default",
                 hotkey=""):
        self.terminal=terminal  # type: Terminal
        self.manager=terminal.clickzonemanager  # type: _ClickZoneManager
        self.center=center  # type: Pos
        self.width=width
        self.height=height

        self.manager.add_clickzone(self, group)

        self.linkup = self.linkdown = self.linkright = self.linkleft = None
        self.hotkey=hotkey

    @property
    def size(self):
        """A tuple of (width, height)."""
        return (self.width, self.height)
    @size.setter
    def size(self, newsize):
        self.width, self.height = newsize

    def on_highlight(self):
        """Called when the mouse cursor hovers over this ClickZone or when
        the user moves the highlight on to this ClickZone with the keyboard,
        either via the arrow keys or by pressing its hotkey."""

    def on_lose_highlight(self):
        """Called when this ClickZone was the highlighted clickzone, but is
        highlighted no longer."""

    def on_click(self):
        """Called when the user clicks on the ClickZone, or presses Enter
        while this ClickZone is highlighted."""

    def on_draw(self, currently_highlighted):
        """Called when .draw() is called on the Terminal this ClickZone is
        on. currently_highlighted will be True if this is the highlighted
        ClickZone.

        Note that having a bunch of ClickZone-s that draw themselves every
        tick is probably going to kill your framerate! Try having a "dirty"
        flag that is set by on_activate, on_highlight, on_lose_highlight, etc...
        and only actually draw yourself when that flag is True.
        """

    def on_activate(self):
        """Called when the group this ClickZone is in is activated."""

    def on_deactivate(self):
        """Called when the group this ClickZone is in is deactivated."""

    def on_terminal_blank(self):
        """Called after the Terminal is blanked. This pretty much only exists so
        that you (or, more likely, the VisibleClickZone) can re-draw yourself
        afterwards; I can't imagine there's any other reason to implement
        this."""

    def on_left_pressed(self):
        """Called when the left arrow key is pressed (or keypad 4 when
        NumLock is not engaged) while this ClickZone is highlighted. By
        default this switches the highlight to the ClickZone in
        self.linkleft; the auto-linker will detect if you have overridden 
        this function and if so will not try to link this ClickZone on that 
        side. Override this by setting self.force_link_left to True."""
        self.manager.highlight(self.linkleft)

    def on_right_pressed(self):
        """Called when the right arrow key is pressed (or keypad 4 when
        NumLock is not engaged) while this ClickZone is highlighted. By
        default this switches the highlight to the ClickZone in
        self.linkright; the auto-linker will detect if you have overridden 
        this function and if so will not try to link this ClickZone on that 
        side. Override this by setting self.force_link_right to True."""
        self.manager.highlight(self.linkright)

    def on_up_pressed(self):
        """Called when the up arrow key is pressed (or keypad 4 when
        NumLock is not engaged) while this ClickZone is highlighted. By
        default this switches the highlight to the ClickZone in
        self.linkup; the auto-linker will detect if you have overridden 
        this function and if so will not try to link this ClickZone on that 
        side. Override this by setting self.force_link_up to True."""
        self.manager.highlight(self.linkup)

    def on_down_pressed(self):
        """Called when the left arrow key is pressed (or keypad 4 when
        NumLock is not engaged) while this ClickZone is highlighted. By
        default this switches the highlight to the ClickZone in
        self.linkleft; the auto-linker will detect if you have overridden 
        this function and if so will not try to link this ClickZone on that 
        side. Override this by setting self.force_link_left to True."""
        self.manager.highlight(self.linkdown)

class _Cell:
    """A single cell in a terminal. Contains the character that's there,
    the foreground and background color, whether or not the cell has been
    updated since the last time the terminal has been blitted, etc..."""

    def __init__(self, terminal):
        self.terminal = terminal
        self.character = ' '

        self.fgcolor = None
        self.bgcolor = None
        self.font = None

        self.italic = False
        self.bold = False
        self.underline = False

        #Cursors set this to True as they write to cells; used by the backend to
        #not redraw cells that have not changed. Backends are under no
        #obligation to respect or reset this, so don't rely on it for anything.
        self.dirty = False

    @property
    def character(self):
        return self._character
    @character.setter
    def character(self,newchar):
        if not newchar: newchar = " "
        self._character = newchar
        self.dirty = True

    @property
    def fgcolor(self):
        if self._fgcolor is None:
            return self.terminal._fgcolor
        else:
            return self._fgcolor

    @fgcolor.setter
    def fgcolor(self, newfgcolor):
        self._fgcolor = _color_name_conversion(newfgcolor)
        self.dirty=True

    @property
    def bgcolor(self):
        if self._bgcolor is None:
            return self.terminal.bgcolor
        else:
            return self._bgcolor

    @bgcolor.setter
    def bgcolor(self, newbgcolor):
        self._bgcolor = _color_name_conversion(newbgcolor)
        self.dirty=True

class Keypress(collections.namedtuple("Keypress", ["key", "shift", "ctrl",
                                                   "alt", "meta"])):
    pass

class Backend(abc.ABC):
    """The thing that actually translates a Terminal into pictures on a
    user's screen."""

    @abc.abstractmethod
    def draw(self):
        """Make the terminal show up on the screen, doing whatever needs to
        happen to make it actually visible to the user (i.e. clearing old
        debris off the screen, flipping buffers, stuff like that)"""
        pass

    @abc.abstractmethod
    def get_characters(self):
        r"""Get keypresses from the keyboard for purposes of putting
        characters on an InputCursor line. Returns a list of one-character
        strings representing each symbol-producing key (i.e. not arrow keys)
        pressed since the last call to this function.

        Alphanumeric and symbol keys should obviously correspond to their
        respective character. Pressing enter should be represented by \n
        ( chr(10) ), tab with \t, delete with \x7F, and backspace with \x08.

        All other control buttons (ex. arrow keys) will be handled through
        the get_keypresses method."""

    @abc.abstractmethod
    def get_keypresses(self, exclude_characters=True):
        """Return a list of Keypress-es, representing keys the user has
        pressed since the last call to this function in the order they were
        pressed. If exclude_characters is True, which it is by default,
        this should *not* include presses that produce characters in
        get_characters()'s return list.

        This is meant as a way for applications to receive non-textual
        keypress info (i.e. a game that uses WASD for movement) as well as
        for textual applications to do things like move the input cursor with
        the arrow keys.
        
        The Keypress this returns is a namedtuple of (key, shift, ctrl, alt,
        meta) Key is a string from keypress_code_set; should be
        self-explainatory. The rest are bools represneting whether or not
        that modifier key was pressed along with the key."""

    @abc.abstractmethod
    def get_mouse(self):
        """Return the current position of the mouse cursor in cell
        coordinates (from (0, 0) to (W, H).) Not
        required; return (-1, -1) to signify that it isn't implemented."""

    @abc.abstractmethod
    def get_left_click(self):
        """Return True if the left mouse button has been pressed _and released_
        since the last time this function was called - NOT -  if it's currently
        being pressed. If not, or if your backend doesn't support the mouse,
        return False."""

    @abc.abstractmethod
    def get_right_click(self):
        """Return True if the _right_ mouse button has been pressed _and
        released_  since the last time this function was called - NOT -  if
        it's currently being pressed. If not, or if your backend doesn't
        support the mouse, return False."""

    @abc.abstractmethod
    def px_to_cell(self, pxpos):
        """Translate pixel-space coordinates to the coordinates of the cell
        the given pixel is in. Raise NotImplementedError if this is
        unavailable, such as with the stdio backend that has no graphical
        backing."""

    @abc.abstractmethod
    def cell_to_px(self, pos):
        """Gives the pixel-space coordinates of the top left corner of the
        cell at the given terminal-space coordinates. Raise
        NotImplementedError if this is unavailable, such as with the stdio
        backend that has no graphical backing.

        If the coordinate values are not integers, the part after the decimal
        place is treated as a fraction of the cell width or height; i.e.

        (5,5) = The top left corner of cell (5,5)
        (5.5, 5.5) = The center of cell (5,5)
        (5.99, 5.5) = The bottom-center of cell (5,5)
        (5.99, 5.99) = The bottom-right corner of cell (5,5)
        """

class Hooks:
    """Data structure for supporting the Terminal's need to have a dict of
    lists of callables that it can call all at once."""

    def __init__(self, hooks):
        self.backing = {hook : list() for hook in hooks}

    def __repr__(self):
        lines=[]
        for thehook in self.backing:
            lines.append(f"{thehook}:")
            for thecback in self.backing[thehook]:
                lines.append(f"\t{thecback}")

    def fire(self, hook, *args):
        """Call all registered callbacks for the given hook."""
        for thecback in self.backing[hook]:
            thecback(*args)

    def clear(self):
        """Unregister all hooks."""
        for thelist in self.backing.values():
            thelist.clear()

    def register(self, cback, hook=None):
        """Register the given callable for the given hook. If none is provided,
        infer it from the callable's .__name__. Silently ignores attempts to add
        the same callback twice."""
        if hook is None: hook = cback.__name__
        if cback not in self.backing[hook]:
            self.backing[hook].append(cback)

    def unregister(self, cback, hook=None):
        """Remove the given callable from the given hook. If none is provided,
        infer it from the callable's .__name__. Silently ignores attempts to remove
        callbacks that were never added or already removed.

        Does NOT search the hook database for all references to cback if a hook name
        is not provided. If you registered a function for two different hooks, remove
        it with the same hook names given."""
        if hook is None: hook = cback.__name__
        #If you're wondering why we're using a list instead of a set, it's because that doesn't work.
        #See https://stackoverflow.com/questions/53984772/id-of-bound-method-changing-mysteriously
        try:
            self.backing[hook].remove(cback)
        except ValueError:
            pass

    def register_all_on(self, obj):
        """Equivalent to calling register on every method on the given object that is
        named after a hook.

        Using this is disrecommended in classes designed to be subclassed; the subclass may have hooks it doesn't
        want registered when you register yours."""
        attrs = dir(obj)
        for hook_name in set(self.backing).intersection(attrs):
            cback = getattr(obj, hook_name)
            if cback not in self.backing[hook_name]:
                self.backing[hook_name].append(cback)

    def unregister_all_on(self, obj):
        """Equivalent to calling unregister on every method on the given object that is
        named after a hook."""
        attrs = dir(obj)
        for hook_name in set(self.backing).intersection(attrs):
            try:
                self.backing[hook_name].remove(getattr(obj, hook_name))
            except ValueError:
                pass

#TODO: Make the Terminal handle picking & unpickling correctly by not pickling its backend and getting a new one when
# unpickled
class Terminal:
    """Represents a virtual terminal; a grid of Unicode characters that is
    presumably going to be displayed on a screen somewhere (though you can
    also make terminals with no intention of ever blitting them to a real
    display device.)

    A Terminal is also a container; myterminal[x, y] gives the Cell object at
    (x,y). Setting items in the terminal is not supported; set the Cell's
    attributes to change the displayed character or color, etc...

    The Terminal also supports slicing; myterminal[(5, 5) : (10, 10)] gives
    you the cells in the square whose top left corner is (5,5) and bottom
    right corner is (10,10). myterminal[::(2,4)] gives you every other cell
    in every other row. The step parameter can be an integer [::5] is
    equivalent to [::(5,5)] but the start and stop must be 2-tuples or None.

    It can also be iterated over, giving every cell in left to right,
    top to bottom, row-major order. I.e. a 3x3 terminal will give
    the cell at (0,0), (1,0), (2,0), (0, 1), (1, 1), (1,2), etc...Slice
    results also come out in this order.

    If font is None, PyConsoleGraphics picks a default font. Otherwise it should
    be the name of an installed font or the full path to a TrueType font file.
    Note that the default font is chosen by the backend and may not be
    consistent across different backends.

    backend should be a string that is in pyconsolegraphics.backends or None;
    if it's None, pyconsolegraphics will pick one for you and will raise
    ValueError if none of them appear to work.

    A terminal can also work text I/O object. Though it does not implement
    the full TextIOBase interface, setting sys.stdin and sys.stdout to a
    Terminal should work correctly, and after doing that print() and input()
    can be used to interact with the Terminal just as in a text-mode program.

    Indeed, calling pyconsolegraphics.override_standard_io() will set this up
    for you, allowing two lines of code (the other being
    'import pyconsolegraphics') to seamlessly convert legacy text-mode
    programs to run under pyconsolegraphics.

    To be able to act on global events relating to the terminal, such as the
    terminal scrolling or being about to draw to the screen, put your callback
    in the terminal's .hooks dict. There is also a .register_hook() method that
    makes this slightly more convenient; see its docstring for details.

    The list of hooks:

        * on_scroll(scrollvec)
        Called when the terminal is scrolled with .scroll_down().

        * before_draw()
        Called right before the terminal's contents are rendered to the screen.
        This is intended for Cursor subclasses that want to draw a visible
        cursor character on the screen at their position.

        * after_draw()
        Called right after the terminal's contents are rendered to the screen.
        This is, again, intended for visible Cursors, so they can put things
        back the way they were before they overwrote what was there with
        their cursor icon.
    """

    def __init__(self, size=(80, 40), font=None, fontsize=16, backend=None,
                 bgcolor="black", fgcolor="white"):
        self.width, self.height = size
        # Note that .cells is in [y][x] order; it's a list of rows, not columns.
        self.cells = [[_Cell(self) for t in range(self.width)]
                      for i in range(self.height)]
        self._bgcolor = _color_name_conversion(bgcolor)
        self._fgcolor = _color_name_conversion(fgcolor)

        #Setting self.font to None signals to the backend to load its default
        # font
        self.font = font
        self.fontsize = fontsize

        self.cursors = []  # type: list[Cursor]
        self.active_input_cursor = None  # type: InputCursor

        self._clickzonemanager = None

        self.autodrawactive = False

        self.hooks = Hooks((
            "on_scroll",
            "before_draw",
            "after_draw",
        ))

        self.requested_backend = backend
        self._initialize_backend(backend)

    def _initialize_backend(self, backend):
        if backend:
            self.backend = backends.backend_funcs[backend](self)
        else:
            for thebend in backend_attempt_order:
                try:
                    self.backend = backends.backend_funcs[thebend](self)
                    break
                except ImportError:
                    #TODO: Turn this in to a warnings.warn
                    print("Failed to load {0} backend".format(thebend))
                    continue
            else:
                raise ImportError("None of the graphics libraries "
                                  "Pyconsolegraphics knows how to use seem to "
                                  "be installed")

    def __getstate__(self):
        """Backends, seeing as they do IO and draw things to the screen and such, don't tend to
        pickle well. So; as it stands, we just delete the backend and create it anew when we're
        unpickled. We may need to give it a way to write out some state later on, but for now..."""
        state = self.__dict__.copy()
        del state["backend"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._initialize_backend(self.requested_backend)

    def __getitem__(self, item):
        if isinstance(item, slice):

            if item.start:
                startx, starty = item.start
            else:
                startx = starty = None

            if item.stop:
                stopx, stopy = item.stop
            else:
                stopx = stopy = None

            try:
                stepx, stepy = item.step
            except TypeError:
                stepx = stepy = item.step

            rows = self.cells[starty : stopy : stepy]
            retlist= [c for row in rows for c in row[startx : stopx : stepx]]
            #It comes out in bottom-to-top, right-to-left order,
            # so we reverse that for consistency's sake
            retlist.reverse()
            return retlist

        else:
            #If it's not a slice we assume its a tuple.
            x, y = item
            try:
                x = math.floor(x)
            except (ValueError, OverflowError):
                raise TypeError("{0} (x of {1}) cannot be converted to integer (did you do term[a, b] instead of term[a : b]?)".format(x, item))
            try:
                y = math.floor(y)
            except (ValueError, OverflowError):
                raise TypeError("{0} (y of {1}) cannot be converted to integer (did you do term[a, b] instead of term[a : b]?)".format(y, item))
            if not 0 <= x < self.width: raise IndexError("{0} is out of bounds on the x axis.".format(item))
            if not 0 <= y < self.height: raise IndexError("{0} is out of bounds on the y axis.".format(item))
            return self.cells[y][x]

    def __iter__(self):
        for therow in self.cells:
            for thecell in therow:
                yield thecell

    def __len__(self):
        return sum(len(row) for row in self.cells)

    @property
    def clickzonemanager(self):
        if not self._clickzonemanager:
            self._clickzonemanager = _ClickZoneManager(self)
        return self._clickzonemanager
    @clickzonemanager.setter
    def clickzonemanager(self, x):
        raise AttributeError("Can't change the clickzone manager of a terminal"
                             "(try .clickzonemanager.switch_to_set() instead.)")

    @property
    def fgcolor(self):
        return self._fgcolor
    @fgcolor.setter
    def fgcolor(self, newfg):
        self._fgcolor =_color_name_conversion(newfg)
        #Any cell that relies on the global fgcolor has changed color...
        for thecell in self:
            if thecell._fgcolor is None:
                thecell.dirty=True

    @property
    def bgcolor(self):
        return self._bgcolor
    @bgcolor.setter
    def bgcolor(self, newbg):
        self._bgcolor =_color_name_conversion(newbg)
        #Any cell that relies on the global bgcolor has changed color...
        for thecell in self:
            if thecell._bgcolor is None:
                thecell.dirty=True

    @property
    def size(self):
        """A tuple of the terminal's width and height, for convenience."""
        return self.width, self.height

    def blank(self):
        """Set the .character of every cell to ' ', and the .fgcolor and
        .bgcolor to None."""
        for therow in self.cells:
            for thecell in therow:
                thecell.bgcolor=None
                thecell.fgcolor=None
                thecell.character=" "

        if self._clickzonemanager:
            for thegroup in self._clickzonemanager.activegroups.values():
                for thezone in thegroup:
                    thezone.on_terminal_blank()

    def scroll_down(self):
        """Scroll the terminal down one line.

        This does change every cell on the terminal so expect the next draw
        call after this to be exceptionally intensive."""

        self.cells.pop(0)
        self.cells.append([_Cell(self) for t in range(self.width)])
        for thecell in self:
            thecell.dirty=True
        if len(self.hooks.backing["on_scroll"]) >= 2:
            print("!!!Multiple on_scroll hooks!!!", file=sys.__stdout__)
        self.hooks.fire("on_scroll", Pos(0, 1))

    def draw(self, called_from_autodraw=False, noflip = False):
        """Command this terminal's backend to draw it to the screen, however
        it accomplishes that.

        If autodraw() has been called on this function, calling draw() on it
        outside of the autodraw thread does nothing."""
        # Having two threads calling backend.draw() often makes very bad
        # things happen.
        if self.autodrawactive and not called_from_autodraw:
            return

        #TODO: Obsoleted by the hook system, remove soon...
        for thecursor in self.cursors:
            thecursor.pre_draw()

        if self._clickzonemanager:
            self._clickzonemanager.draw()

        self.hooks.fire("before_draw")

        self.backend.draw(noflip=noflip)

        self.hooks.fire("after_draw")

    def process(self):
        """Do all the administrative tasks a Terminal has to have done to it
        regularly, such as determining where the mouse is to set ClickZones
        off, and registering keypresses. Ideally you want to call this right
        before you call draw(). Definitely aim for calling this at least 30
        times a second and once for every draw() call."""

        # Don't want autodraw scooping up all the input
        if self.active_input_cursor:
            self.active_input_cursor._process_chars(self.backend.get_characters())
            self.active_input_cursor._process_keys(self.backend.get_keypresses())

        if self._clickzonemanager and self._clickzonemanager.activegroups:
            mpos = self.backend.get_mouse()
            click = self.backend.get_left_click()
            try:
                #If get_mouse isn't implemented it'll just give us (-1,-1)
                moused=self._clickzonemanager.zonemap[mpos]
                self.clickzonemanager.highlight(moused)
            except KeyError:
                pass
            else:
                if click:
                    moused.on_click()

            #This will just return nothing if there's an active input cursor
            presses = self.backend.get_keypresses(False)
            for thepress in presses:
                try:
                    hotkeyedzone=self.clickzonemanager.hotkeymap[thepress]

                except KeyError:
                    #Don't get any funny ideas, this is for speed. Only
                    # left/right/up/down are actually allowed.
                    #Although I may make this part of the spec at some point.
                    #@TODO: Wait, I could just replace this with a dict. Duh.
                    if thepress == "\n":
                        self.clickzonemanager.currently_highlighted.on_click()
                    else:
                        call = "on_{0}_pressed".format(thepress)
                        handler = getattr(self.clickzonemanager.currently_highlighted, call, None)
                        if handler:
                            handler()

                else:
                    self.clickzonemanager.highlight(hotkeyedzone)
                    hotkeyedzone.on_click()


    def write(self, text):
        """Write the given text to the stdio cursor, creating it if it does
        not exist. This is not the recommended way to simply write text to
        the console, see ezmode.writeline for that. This exists so the
        Terminal can be used as a sys.stdout replacement."""
        if not hasattr(self, "stdiocursor"):
            self.stdiocursor = InputCursor(self)

        for thechar in text:
            self.stdiocursor.smart_writechar(thechar)

    @property
    def center(self):
        """A 2-tuple of integers representing the X, Y coordinates of the
        cell in the center of the terminal, or an approximation thereof if
        the terminal is an even number of cells in size."""
        x = self.width // 2 - 1
        y = self.height // 2 - 1

        return Pos(x, y)

    @property
    def topleft(self):
        """The 2-tuple (0, 0), in other words the coordinates of top left
        corner of the terminal."""
        return Pos(0, 0)

    @property
    def topright(self):
        """The 2-tuple (W, 0), where W is the width of the terminal,
        in other words the coordinates of the top right corner of the
        terminal."""
        return Pos(self.width - 1, 0)

    @property
    def bottomleft(self):
        """The 2-tuple (0, H - 1), where H is the height of the terminal,
        in other words the coordinates of the bottom left corner of the
        terminal."""
        return Pos(0, self.height - 1)

    @property
    def bottomright(self):
        """The 2-tuple (W - 1, H - 1), where H and W are the height and width
        of the
        terminal. In other words coordinates of the bottom right corner of the
        terminal."""
        return Pos(self.width - 1, self.height - 1)

    @property
    def topcenter(self):
        """The 2-tuple (X, 0) where X is (an approximation of) the width-wise
        center of the terminal."""
        return Pos(self.width // 2 - 1, 0)

    @property
    def bottomcenter(self):
        """The 2-tuple (X, H - 1) where X is (an approximation of) the
        width-wise center of the terminal, and H is the height of the
        terminal."""

        return Pos(self.width // 2 - 1, self.height - 1)

    @property
    def centerleft(self):
        """The 2-tuple (0, Y) where Y is (an approximation of) the height-wise
        center of the terminal."""

        return Pos(0, self.height // 2)

    @property
    def centerright(self):
        """The 2-tuple (W - 1, Y) where Y is (an approximation of) the
        width-wise center of the terminal and W is the height of the terminal."""

        return Pos(self.width - 1, self.height // 2)

    def readline(self):
        """A small part of the TextIO interface, which just so happens to be
        the part that gets called on sys.stdio by input(). In other words
        this is what lets input() be used to get input from the terminal's
        stdiocursor when the terminal is replacing stdin."""
        if not hasattr(self, "stdiocursor"):
            self.stdiocursor = InputCursor(self)

        return self.stdiocursor.get_line()

    def flush(self):
        """Called by print() on stdout under certain conditions."""
        #@TODO: This probably ought to just be a stub...
        self.draw()


def autodraw(term, fps=30):
    """Spawn a thread that draws the given terminal every 1/fps seconds,
    so you don't have to worry about calling .draw(); just put the characters
    you want on the terminal and they'll magically appear on the user's screen!
    Returns the drawing thread; feel free to just throw it out, it'll keep
    working.
    :type term Terminal
    """

    def drawfunc():
        while True:
            term.draw(called_from_autodraw=True)
            #@TODO: Implement real FPS management code, not this shit
            time.sleep(1 / fps)

    thethread = threading.Thread(target=drawfunc,
                                 name="pyconsolegraphics_autodraw",
                                 daemon=True)
    thethread.start()
    term.autodrawactive = True
    return thethread


def override_standard_io(**kwargs):
    """Set pyconsolegraphics up automatically so that you can use print() and
    input() just like in a console-mode application, but without the
    inconveniences that come with actually being a console-mode application.

    This creates a Terminal object, sets stdout and stdin to it, and then
    calls autodraw on it; no further manipulation is necessary, and it'll
    go away when the main program terminates.

    Takes the same keyword arguments the Terminal class takes for configuring
    the window, i.e. size, font, color, etc... or those can be omitted to
    leave them at defaults."""

    sys.stdin = sys.stdout = theterm = Terminal(**kwargs)
    autodraw(theterm)

def _color_name_conversion(x):
    """If x is a tuple, return x.
    If x is None, return None.
    If x is an int, assume it's a 0xRRGGBB style color
    If x is a string:
        if x is in colors, return colors[x],
        if x looks like a hexadecimal value, interpret that as if it were an int
        otherwise raise ValueError."""
    def fail(): raise ValueError("{0!r} is not a valid color specifier.".format(x))
    try:
        return colors[x]
    except KeyError:
        if isinstance(x, (str, int)):
            if isinstance(x, str):
                strippedx=x.strip("#$%&0xX")
                if len(strippedx) != 6:
                    fail() #Wrong number of chars to be an RRGGBB string
                try:
                    colorint = int(strippedx, 16)
                except ValueError:
                    fail() #Stripped known extra stuff around the RRGGBB, but still couldn't convert to int
            else:
                colorint = x

            if colorint > 0xFFFFFF:
                fail() #Color integer too high to be RRGGBB (> 0xFFFFFF)

            r = colorint >> 16 & 0xFF
            g = colorint >> 8 & 0xFF
            b = colorint & 0xFF
            return(r,g,b)

        elif isinstance(x, tuple):
            if len(x) in (3, 4) and all(isinstance(v, int) for v in x):
                return x
            else:
                fail() #Not a 3-tuple of integers

        elif x is None:
            return x

        else:
            #maybe it's something that can be converted to a tuple?
            try:
                return _color_name_conversion(tuple(int(v) for v in x))
            except TypeError:
                fail() #Isn't anything I know what to deal with, and can't convert to something I do

    except TypeError: #raised if x is unhashable
        #Might be a numpy array...
        try:
            return _color_name_conversion(tuple(int(v) for v in x))
        except TypeError:
            fail() #Isn't anything I know what to deal with, and can't convert to something I do