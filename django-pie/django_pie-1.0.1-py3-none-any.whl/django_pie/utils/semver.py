# coding: utf-8


class Version:
    def __init__(self, a: int, b: int, c: int):
        self.a = a
        self.b = b
        self.c = c


def parse(version: str):
    v = version.split('.')
    return Version(int(v[0]), int(v[1]), int(v[2]))


def compare(version1: str, version2: str):
    v1 = parse(version1)
    v2 = parse(version2)
    if v1.a >= v2.a and v1.b >= v2.b:
        if v1.c > v2.c:
            return 1
        elif v1.c == v2.c:
            return 0

    return -1
