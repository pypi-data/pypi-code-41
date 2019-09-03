#coding: utf8
#author: hepochen@gmail.com
from __future__ import absolute_import
import os, re


def get_valid_docker_containers():
    # with pid
    containers = {}
    cmd = os.popen("docker ps")
    cmd_result = cmd.read().strip()
    lines = cmd_result.split('\n')
    if not lines:
        return {}
    lines = lines[1:]
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = re.split('\s{3,}', line)
        name = parts[-1]
        image = parts[1]
        status = parts[4]
        sub_cmd = os.popen("docker inspect --format '{{.State.Pid}}' %s"%name)
        sub_cmd_result = sub_cmd.read().strip()
        try:
            container_pid = int(sub_cmd_result)
            containers[name] = dict(
                pid = container_pid,
                name = name,
                image = image,
                status = status
            )
        except:
            continue
    return containers



