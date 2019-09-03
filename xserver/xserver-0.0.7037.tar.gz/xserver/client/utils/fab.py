# coding: utf8
from fabric.api import sudo, run, put, env
from fabric.network import disconnect_all
import sys
import os
import time
from StringIO import StringIO
from xserver.utils import to_bytes

silent_out = StringIO()

root = os.path.dirname(os.path.dirname(__file__))


def run_silent(command):
    run(command, stdout=silent_out)


def run_and_get_info(command):
    stdout = StringIO()
    run(command, stdout=stdout)
    info = stdout.getvalue()
    return info # 得到反馈输出的信息



def put_file(local_path, remote_path):
    filepath = os.path.join(root, local_path)
    put(filepath, remote_path, use_sudo=True)



def put_file_content(file_content, remote_path, use_sudo=True):
    file_content = to_bytes(file_content)
    f = StringIO(file_content)
    put(f, remote_path, use_sudo=use_sudo)



def apt(package_name):
    if isinstance(package_name, (list, tuple)):
        package_names = package_name
        for package_name in package_names:
            run('apt-get install -y %s' % package_name)
    else:
        run('apt-get install -y %s' % package_name)


def make_env(host_ip, user='root', password=None, create_tmp_host_file=True):
    disconnect_all()
    env.user = user
    if password:
        env.password = password
        # like env.passwords = {'root@xx.xx.xx.xx:22': 'xxxxx'}
    env.host_string = host_ip.strip()
    env.disable_known_hosts = True

    if create_tmp_host_file:
        try:
            put_file_content(host_ip, '/tmp/__current_connected_host.txt')
        except:
            pass


def run_cmds(cmds):
    if not isinstance(cmds, (list, tuple)):
        cmds_list = cmds.split('\n')
        cmds = []
        for cmd in cmds_list:
            cmd = cmd.strip()
            if cmd:
                cmds.append(cmd)
    for cmd in cmds:
        cmd = cmd.strip()
        if not cmd:
            continue
        run(cmd)


CSI="\x1B["
RED = CSI+"31;40m"
GREEN = CSI+'32;40m'
RESET =CSI+"m"

def print_color(color, strings):
    if color == 'green':
        print GREEN + strings + RESET
    elif color == 'red':
        print RED + strings + RESET
    else:
        print strings