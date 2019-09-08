""" ANSI Escape Color Code.

Define some ANSI escape code for shell output color.
"""
BLACK="0;30"
DARK_GRAY="1;30"
CYAN="0;36"
LIGHT_CYAN="0;96"
LIGHT_GRAY="0;37"
RED="0;31"
GREEN="0;32"
LIGHT_GREEN="0;92"
ORANGE="0;33"
YELLOW="1;33"
LIGHT_YELLOW="0;93"
BLUE="0;34"
LIGHT_BLUE="0:94"
PURPLE="0;35"
WHITE="1;37"
BRIGHT_WHITE="0;97"


def print_color(skk, color=WHITE, underline=False, bold=False):
    """ Color coded print out to stdout. """
    decoration = ';4' if underline else ''
    decoration = ';1' if bold else decoration
    print("\033[{}{}m {}\033[00m".format(color, decoration, skk))

