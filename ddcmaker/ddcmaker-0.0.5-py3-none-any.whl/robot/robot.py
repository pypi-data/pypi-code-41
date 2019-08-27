# import cv2
import time
# import LSC_Client
from robot import LSC_Client

import threading

from inspect import signature
from functools import wraps


def typeassert(*type_args, **type_kwargs):
    def decorate(func):
        sig = signature(func)
        bound_types = sig.bind_partial(*type_args, **type_kwargs).arguments

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_values = sig.bind(*args, **kwargs)
            for name, value in bound_values.arguments.items():
                if name in bound_types:
                    if not isinstance(value, bound_types[name]):
                        raise TypeError('Argument {} must be {}'.format(name, bound_types[name]))
            return func(*args, **kwargs)

        return wrapper

    return decorate


lsc = LSC_Client.LSC_Client()


class robot(object):
    lsc.MoveServo(6, 1500, 1000)
    lsc.MoveServo(7, 1500, 1000)
    time.sleep(1.1)

    def up(self, step):
        lsc.RunActionGroup(0, step)
        lsc.WaitForFinish(int(step * 20000))

    def check(self, step):
        lsc.RunActionGroup(188, step)
        lsc.WaitForFinish(int(step * 20000))

    def forward(self, step):
        lsc.RunActionGroup(1, step)
        lsc.WaitForFinish(int(step * 20000))

    def backward(self, step):
        lsc.RunActionGroup(2, step)
        lsc.WaitForFinish(int(step * 20000))

    def left(self, step):
        lsc.RunActionGroup(3, step)
        lsc.WaitForFinish(int(step * 20000))

    def right(self, step):
        lsc.RunActionGroup(4, step)
        lsc.WaitForFinish(int(step * 20000))

    def circle(self, step, radius):
        for j in range(0, step):
            for i in range(0, 10):
                self.right(2)
                self.forward(radius)
        self.up(1)

    def shaking_head(self, step):
        lsc.RunActionGroup(50, step)
        lsc.WaitForFinish(int(step * 20000))

    def nod(self, step):
        lsc.RunActionGroup(51, step)
        lsc.WaitForFinish(int(step * 20000))


# ------------福利区，暂时不对外开放--------------
'''
还没想好写些什么
'''
from showlib import showlib


class show(object):
    lsc.RunActionGroup(0, 1)
    lsc.WaitForFinish(int(20000))

    def JNstyle(self):
        showlib.jiangnanstyle()

    def smallapple(self):
        showlib.smallapple()

    def hiphop(self):
        showlib.hiphop()

    def lasong(self):
        showlib.lasong()

    def feelgood(self):
        showlib.feelgood()


# ----------------测试区------------------
from voice import voicelist
class speak(object):
    def speak(self, viocenum):
        if viocenum >= 48 or viocenum <= 25:
            return "超出语音模块区域"
        else:
            lsc.RunActionGroup(viocenum, 1)
            vlist=voicelist()
            lsc.WaitForFinish(int(20000))
            time.sleep(int(vlist.voicelist()[viocenum]))

