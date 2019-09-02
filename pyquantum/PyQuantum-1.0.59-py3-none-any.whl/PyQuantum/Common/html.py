import webbrowser
from math import sqrt


def DOT():
    return " &middot; "

def SQRT(s):
    return "&radic;" + """<span style=\"text-decoration:overline;\">""" + str(s) + " </span>"

def SUB(s):
    return "<sub>" + str(s) + "</sub>"

def a_cross(ph):
    return sqrt(ph + 1)


def a(ph):
    return sqrt(ph)


def A_CROSS(s):
    return SQRT(str(int(a_cross(s)**2)))
