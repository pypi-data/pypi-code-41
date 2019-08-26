# coding=utf-8
import os
import sys
import subprocess
import platform

def platform_hitc():
    hitc_path = {
        "Windows":"hitc.exe",
        "Linux":"hitc"
    }.get(platform.system(),"hitc")

    def hitc_subprocess(xargs):
        xargs.insert(0,hitc_path)
        child1 = subprocess.Popen(xargs, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True, universal_newlines = True)

        #非阻塞
        return child1.stdout.read()


    return hitc_subprocess

def platform_hitc_block():
    hitc_path = {
        "Windows":"hitc.exe",
        "Linux":"hitc"
    }.get(platform.system(),"hitc")

    def hitc_subprocess(xargs):
        xargs.insert(0,hitc_path)
        child1 = subprocess.Popen(xargs, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True, universal_newlines = True)

        # # 阻塞
        result = child1.communicate(input=None)
        # (k --> ('model create failed, error: GPU model name already exist.\n', None))
        return result[0]

    return hitc_subprocess

hitc = platform_hitc_block()

hitc_block = platform_hitc_block()



# if __name__ == "__main__":
#     hitc(["-a","-b","-c"])