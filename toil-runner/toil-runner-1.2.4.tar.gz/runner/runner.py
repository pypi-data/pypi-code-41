
import logging
import pwd
import sys
import time
import os
import datetime
import grp
import subprocess
import traceback

import wrapt
import docker
import inspect
import getpass


from sarge import run, Capture


@wrapt.decorator
def decorator_wrapt(wrapped, instance, args, kwargs):
    excepted_keys = ['image', 'volumes']
    excepted_types = [str, dict]
    wrapped_obj = wrapped(*args, **kwargs)
    for key, check_type in zip(excepted_keys, excepted_types):
        if not hasattr(instance, key):
            raise ValueError(str(instance.__class__)+"not" + key)
        if check_type is str:
            check_type = unicode
        if not isinstance(getattr(instance, key), check_type):
            #int(type(getattr(instance, key)))
            raise ValueError("type incorret class {} key:{} values:{} check_type{} ".format(
                str(instance.__class__), key, type(getattr(instance, key)), check_type))

    # if mount path not exist , raise exception
    for key in getattr(instance, 'volumes').keys():
        if not os.path.exists(key):
            raise ValueError("volumes path error")

    # if docker image not exist , raise exception
    client = docker.from_env(timeout=1000)
    try:
        client.images.get(getattr(instance, "image"))
    except docker.errors.ImageNotFound as E:
        raise ValueError(str(getattr(instance, "image"))+"not found")
    return wrapped_obj


def docker_runner_method(cls, command, jobname, image, volumes, privileged=True, remove=True, debug=False, enable_std=False, ipc_mode=None):
    client = docker.from_env()

    volumes['/etc/localtime'] = {
        "bind": "/etc/localtime",
        "mode": "rw"
    }
    cls.log("Runtime." + jobname + ".Start=" + str(time.time()))
    try:
        cls.log('start run'+' '.join(command))
        if not debug:
            group_add = [g.gr_gid for g in grp.getgrall(
            ) if getpass.getuser() in g.gr_mem]
            gid = pwd.getpwnam(getpass.getuser()).pw_gid
            group_add.append(gid)
            if not ipc_mode:
                contains = client.containers.run(image, command, network_mode='host', volumes=volumes, privileged=privileged,
                                                 user=pwd.getpwnam(getpass.getuser()).pw_uid, group_add=group_add, detach=True)
            else:
                contains = client.containers.run(image, command, network_mode='host', volumes=volumes, privileged=privileged,
                                                 user=pwd.getpwnam(getpass.getuser()).pw_uid, group_add=group_add, detach=True, ipc_mode=ipc_mode)
            stream = contains.logs(stream=True)
            buffer_logs = list()
            # can't user lambada (lazy)
            for item in stream:
                buffer_logs.append(item)
            if contains.wait() != 0:
                cls.log(''.join(buffer_logs), level=logging.ERROR)
                contains.remove(v=True)
                raise ValueError("Non Zero return")
            if enable_std:
                cls.log(''.join(buffer_logs))
            contains.remove(v=True)
        else:
            cls.log(' '.join(command))
    except Exception as e:
        cls.log(str(e), level=logging.ERROR)
        raise ValueError("Exception")
    cls.log("Runtime." + jobname+".End=" + str(time.time()))

# This decorator must wrap  run method in class


def docker_runner(jobname, privileged=True, remove=True, debug=False, enable_std=False):
    @wrapt.decorator
    def inner_runner(wrapped, instance, args, kwargs):
        if instance is None:
            raise ValueError("instance is not class")
        command = wrapped(*args, **kwargs)

        if not isinstance(command, list):
            raise ValueError("not list instance")

        for exce_name in command:
            if not (isinstance(exce_name, str) or isinstance(exce_name, unicode)):
                raise ValueError("list element is not str")
        docker_runner_method(instance, command, jobname, instance.image,
                             instance.volumes, privileged, remove, debug, enable_std)
    return inner_runner


def adpater_logging(msg, level):
    return logging.log(level, msg)


def sarge_runner(jobname, debug=False, enable_std=False, log_command=True):
    @wrapt.decorator
    def inner_runner(wrapped, instance, args, kwargs):
        if instance:
            log_func = instance.log
        else:
            log_func = adpater_logging
        command = wrapped(*args, **kwargs)
        command_line = ' '.join(command)
        log_func("Runtime." + jobname + ".Start=" +
                 str(time.time()), level=logging.INFO)
        start = datetime.datetime.now()
        try:
            if not debug:
                process = run(command_line, async_=False,
                              stdout=Capture(), stderr=Capture())
                ret_code = any(process.returncodes)

                if log_command:
                    log_func(command_line, level=logging.INFO)

                if enable_std:
                    log_func(process.stdout.text, level=logging.INFO)

                if ret_code:
                    log_func(process.stderr.text, level=logging.ERROR)
                    raise ValueError("return code not equl zero:")
            else:
                log_func(command_line, level=logging.INFO)

        except Exception as E:
            log_func(command_line, level=logging.ERROR)
            log_func(str(E), level=logging.ERROR)
            raise ValueError("Exception")

        log_func("Runtime" + jobname+"End=" +
                 str(time.time()), level=logging.INFO)
        end = datetime.datetime.now()
        elapsed = end - start
        if not instance:
            log_func("elapsed time:" +
                     str(elapsed.total_seconds()), logging.INFO)
            return elapsed.total_seconds()
    return inner_runner


def subprocess_runner(jobname, enable_std=False, debug=False):
    @wrapt.decorator
    def inner_runner(wrapped, instance, args, kwargs):
        if instance:
            log_func = instance.log
        else:
            log_func = adpater_logging
        command = wrapped(*args, **kwargs)
        command_line = ' '.join(command)
        start = datetime.datetime.now()
        log_func("Runtime." + jobname + ".Start=" +
                 str(time.time()), level=logging.INFO)
        try:
            if not debug:
                # excute real command
                process = subprocess.Popen(
                    command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                out, err = process.communicate()
                if enable_std:
                    # log process stdout
                    log_func(out, level=logging.INFO)
                if process.returncode:
                    log_func(err, level=logging.ERROR)
                    raise ValueError("None zero return")

            else:
                # log  execute command
                log_func(command_line, level=logging.INFO)
        except Exception as E:
            log_func(command_line, level=logging.ERROR)
            log_func(str(E), level=logging.ERROR)
            raise ValueError("Exception")
        log_func("Runtime" + jobname+"End=" +
                 str(time.time()), level=logging.INFO)
        end = datetime.datetime.now()
        elapsed = end - start
        if not instance:
            return elapsed.total_seconds()
    return inner_runner


__all__ = ['sarge_runner', 'docker_runner']
