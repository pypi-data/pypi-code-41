import colorama


"""
from coloramaeasy import print_colors
>>> print_colors("{RED}Hello{BGRED}What{WHITE}OK")                                                                     
>>> print_colors("{RED}Hello{BGRED}What{RESET}{WHITE}OK")                                                              
"""

NAMES_TO_COLORS = {}
for attrname in dir(colorama.Fore):
    if attrname.isupper():
        NAMES_TO_COLORS[attrname] = getattr(colorama.Fore, attrname)

for attrname in dir(colorama.Back):
    if attrname.isupper():
        NAMES_TO_COLORS["BG"+attrname] = getattr(colorama.Back, attrname)

NAMES_TO_COLORS['RESET'] = colorama.Style.RESET_ALL


def format(s):
    return s.format(**NAMES_TO_COLORS)

def print_colors(s):
    print(format(s))