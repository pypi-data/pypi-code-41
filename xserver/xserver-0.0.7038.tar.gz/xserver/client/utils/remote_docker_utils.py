# coding: utf8
# 从远程, 对服务器端的 docker 的操作
from xserver.client.utils.fab import *

def show_docker_status():
    run('docker images')
    run('docker ps -a')
    run('python /server/run_docker.py status')



def set_env_file(name, content):
    # 一些 env 环境的设定, 在/home/env 这个目录下
    sudo('mkdir -p /home/env')
    run('echo %s > /home/env/%s'%(content, name))



def run_in_docker(container_name, command):
    # 在一个具体的容器内运行命令
    # command 本身不能包含单引号
    if command.endswith('.sh') and not 'chmod ' in command:
        real_command = """docker exec %s bash %s""" % (container_name, command)
    else:
        if "'" in command:
            command = '"%s"' % command
        else:
            command = "'%s'" % command
        real_command = """docker exec %s bash -c %s""" % (container_name, command)
    run(real_command)


def copy_file_and_run_it_in_docker(container_name, filename):
    # filename is under /server
    filepath = os.path.join('/server', filename)
    filepath_in_docker = os.path.join('/tmp', filename)
    command_for_copy_file = 'docker cp %s %s:%s ' % (filepath, container_name, filepath_in_docker)
    run(command_for_copy_file)
    run_in_docker(container_name, "chmod +x %s" % filepath_in_docker) # docker 内该路径添加可执行的属性
    run_in_docker(container_name, filepath_in_docker) # 执行这个文件


def set_docker_evn(container_name, content):
    # 设定容器运行是，一些额外的参数，比如内存 ip
    set_env_file(container_name, content)

def set_docker_ip(container_name, docker_ip):
    # 设定容器运行时绑定的ip
    env_name = '%s_ip' % container_name
    set_env_file(env_name, docker_ip)




