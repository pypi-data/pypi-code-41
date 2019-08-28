import os
import sys
import subprocess
import logging
import re
import json


def __suc(procename):
    logging.warning("[kill_process] kill process <%s> suc!", procename)


def __not():
    logging.warning("[kill_process] nothing to kill")


def kill_process(procename):
    cmd_killall = "killall %s" % procename
    ret = subprocess.Popen(cmd_killall, shell=True,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    sout, serr = ret.communicate()
    if ret.returncode == 0:
        __suc(procename)
    else:
        cmd_findone = "ps -ef | grep %s" % procename
        ret = subprocess.Popen(cmd_findone, shell=True,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        sout, serr = ret.communicate()
        proce_list = re.split("\n+", sout.decode("utf-8"))
        if len(proce_list) > 1:
            for proce in proce_list:
                infos = re.split("\s+", proce)
                if procename in infos\
                        and ("grep" not in infos)\
                        and (__file__ not in infos):
                    ret = subprocess.Popen("kill -9 %s" %
                                           str(infos[2]), shell=True)
                    retcode = ret.wait()
                    if (retcode == 0):
                        __suc("PID:%s" % str(infos[2]))
        else:
            __not()


if __name__ == "__main__":
    proc_name = sys.argv[1]
    kill_process(proc_name)
