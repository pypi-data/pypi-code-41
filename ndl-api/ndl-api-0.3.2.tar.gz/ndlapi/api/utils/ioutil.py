"""
NeurodataLab LLC 12.04.2019
Created by Andrey Belyaev
"""


def read_binary(path):
    with open(path, "rb") as binput:
        return binput.read()
