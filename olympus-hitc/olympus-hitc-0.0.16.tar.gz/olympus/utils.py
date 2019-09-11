# coding=utf-8
import os
import sys
import subprocess
import platform


def _platform():
    hitc_path = {
        "Windows": "hitc.exe",
        "Linux": "hitc"
    }

    return hitc_path.get(platform.system(), "hitc")


def _hitc():
    hitc_path = _platform()
    
    def hitc_subprocess(xargs):
        xargs.insert(0, hitc_path)
        xargs = " ".join(xargs)

        child1 = subprocess.Popen(xargs,
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE,
                                  shell=True,
                                  universal_newlines=True)

        # 非阻塞
        return child1.stdout.read()

    return hitc_subprocess




def _hitc_block():
    hitc_path =_platform()

    def hitc_subprocess(xargs):
        xargs.insert(0, hitc_path)
        xargs = " ".join(xargs)

        child1 = subprocess.Popen(xargs,
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE,
                                  shell=True,
                                  universal_newlines=True)

        # 阻塞
        result = child1.communicate(input=None)
        # ('model create failed, error:nGPU model name already exist.\n', None)
        return result[0]


    return hitc_subprocess


def _x_hitc_block():
    hitc_path =_platform()

    def hitc_subprocess(xargs):
        xargs.insert(0, hitc_path)
        xargs = " ".join(xargs)
        child1 = subprocess.Popen(xargs,
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE,
                                  shell=True,
                                  universal_newlines=True)

        # 阻塞
        result = child1.communicate(input="yes")
        # ('model create failed, error:nGPU model name already exist.\n', None)
        return result[0]


    return hitc_subprocess

hitc = _hitc_block()
hitcx = _x_hitc_block()

# if __name__ == "__main__":
#     hitc(["-a","-b","-c"])
