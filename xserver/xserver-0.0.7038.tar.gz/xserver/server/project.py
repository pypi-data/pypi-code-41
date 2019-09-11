# coding: utf8
from __future__ import absolute_import, print_function
import os
import re
import socket
from xserver.utils.command import run_commands
from xserver.utils.docker_utils import get_image_names, get_containers, has_image, update_docker_ips
from xserver.utils.cli_color import print_with_color
from xserver.utils.ip import get_local_net_ips_data
from xserver.utils.path import write_file

projects_root = '/home/run'


def run_project(project_dir):
    # 启动一个容器
    # project_dir is like   /home/working/zrey_farbox, and the zrey_farbox is a container name too.

    # project_dir 也可以只是 name
    if '/' not in project_dir:
        project_dir = '/home/run/' + project_dir

    if not os.path.isdir(project_dir):
        return print_with_color('project dir is empty', 'red') # ignore

    # 直接ignore
    ignore_filepath = os.path.join(project_dir, 'ignore')
    if os.path.isfile(ignore_filepath):
        return print_with_color('%s is not started, ignore file is here'%project_dir, 'red')  # ignore


    # 预处理
    container_name = os.path.split(project_dir)[-1] # 比如 zrey_farbox

    run_container_script_path = os.path.join(project_dir, 'run.sh')
    run_container_tmp_script_path = os.path.join(project_dir, 'run_tmp.sh') # 临时脚本路径，实际上最终运行的，是run.sh 上文本处理过的

    if not container_name:
        return print_with_color('container name is empty', 'red')
    if not os.path.isfile(run_container_script_path):
        return print_with_color('script for runtime is empty', 'red')

    # 从脚本中, 提取 docker 的镜像名, 运行脚本的最后一行，就是镜像的名字
    with open(run_container_script_path) as f:
        image_name = f.read().strip().split('\n')[-1].strip().split(' ')[-1]

    if not image_name:
        return print_with_color('image name for container is not set yet', 'red')

    image_name_without_tag = image_name.split(':')[0]
    try:
        # 尝试更新一个最新的镜像
        run_commands('docker pull %s:latest || echo docker_pull_error' % image_name_without_tag)
    except:
        pass


    #  通过指定镜像的名字
    containers = get_containers() # 当前服务器节点已经存在的容器列表
    if container_name in containers: # 容器已经存在了，ignore，或者需要重启
        container = containers.get(container_name)
        is_live = container.get('is_live', False)
        if is_live:
            print_with_color('%s is on running already' % container_name) # 已经启动了，不处理
        else:
            run_commands('docker start %s' % container_name) # 已经存在容器了，尝试去启动容器
            print_with_color('try to restart %s' % container_name, 'red')
    else:
        if not has_image(image_name):
            # 先创建镜像, 一般都已经放在docker.io 上，直接 pull 下来就可以了
            # 但要看是不是要从本地 build
            run_commands('docker pull %s'%image_name) # 先将镜像从 docker.io 上拉下来

        local_ips_data = get_local_net_ips_data() # 本机的 ip（可访问，非本地
        local_ips = local_ips_data[0]
        local_ip = local_ips[0] if local_ips else None # 本地的ip


        current_connected_host_filepath = '/tmp/__current_connected_host.txt'
        if os.path.isfile(current_connected_host_filepath):
            with open(current_connected_host_filepath) as f:
                _local_ip = f.read().strip()
            if local_ips and _local_ip in local_ips:
                local_ip = _local_ip

        if not local_ip: # 可能是某些vps的原因，不能在 ifconfig 里体现出ip
            local_host_name = socket.gethostname()
            s = re.search(r'\d+-\d+-\d+-\d+', local_host_name)
            if s:
                ip_s = s.group()
                local_ip = ip_s.replace('-', '.')


        # container 指定了一些 ip, 如果本机匹配，就会使用这个指定的 ip 作为路由的转发
        # container 内的 ips 会是一个 list，如果当前的 ip 在这个 list 里，那么 container 就会绑定到这个 ip 上

        # container 指定了 hostname
        # 如果有 ip 匹配到，并且 hostname 内容为 `ip`，则以这个 ip 为 hostname，一般为了 hostname 本身的可解析性
        container_ip_config_filepath = '/home/env/%s_ip' % container_name
        container_ip = None
        if os.path.isfile(container_ip_config_filepath):
            with open(container_ip_config_filepath) as f:
                container_ip = f.read().strip()

        # 默认使用当前container的ip，作为hostname
        container_hostname = container_ip or local_ip

        # 容器运行时，额外的一些设定
        container_more_configs_filepath = '/home/env/%s' % container_name
        container_more_configs = None
        if os.path.isfile(container_more_configs_filepath):
            with open(container_more_configs_filepath) as f:
                container_more_configs = f.read().strip()

        # 得到原始的运行脚本内容
        with open(run_container_script_path) as f:
            script_content = f.read()

        if container_more_configs: # 运行容器时的更多设定
            script_content = script_content.replace(' run -d ', ' run -d %s '% container_more_configs)

        on_main_host = False # 是否 母机 全权限
        if '--net=host' in script_content:
            on_main_host = True

        # 指定了 hostname，但是原来的脚本中则未指定的， 但是--net=host 与 -h 是冲突的
        if container_hostname and '-h ' not in script_content and not on_main_host:
            # 如果有指定 hostname 的，但是脚本里没有-h 指定的，则尝试指定
            # 有特别指定的ip
            script_content = script_content.replace(' run -d ', ' run -d -h %s ' % container_hostname)

        # 给 env 传递 IP 这个变量
        if container_hostname:
            script_content = script_content.replace(' run -d ', ' run -d -e IP=%s ' % container_hostname)

        # 如果有多个 IP, 一般是要在 docker 上 bind 一个 IP 的
        if container_ip:
            bind_ip = True
        elif local_ip and len(local_ips) > 1:
            bind_ip = True
        else:
            bind_ip = False

        if bind_ip and not on_main_host:
            # 这里一定会走 docker 虚拟出来的 network，但这是有性能损耗的；但外部母鸡上，可以绑定全局网卡，但是不能绑定 ip
            # 如果需要最高的性能，在run.sh 里面指定--net=host, 而且通过ENV 的形式，把当前 container 需要传递的 ip 传递进去；
                # 然后包括 nginx、dns 等需要绑定的时候，绑定到对应的 IP 上 （从 ENV 变量中取）
            # 替换原来类似 -p 53:53 的为 -p 外部ip:53:53
            ip_to_bind = container_ip or local_ip
            script_content = re.sub(r'(-p )(\d+:\d+)', '\g<1>%s:\g<2>'%ip_to_bind, script_content)


        # 设定 container_name 如果脚本内容身本没有确定的话
        if ' --name  ' not in script_content:
            script_content = script_content.replace(' run -d ', ' run -d --name %s '%container_name)

        #if ' -m ' in script_content and '--oom-kill-disable' not in script_content:
        #    script_content = script_content.replace(' run -d ', ' run -d --oom-kill-disable ')

        # 替换内容（固定的动态变量）
        script_content = script_content.replace('$name$', container_name)

        # 保存脚本内容 到临时文件
        with open(run_container_tmp_script_path, 'w') as f:
            f.write(script_content)

        print_with_color(script_content, 'green')

        # 运行bash脚本
        run_commands('bash %s'%run_container_tmp_script_path)

        if os.path.exists(run_container_tmp_script_path):
            # 移除临时文件
            os.remove(run_container_tmp_script_path)

    # at last
    # 载入 docker 各个 containers 的 ip 情况
    update_docker_ips()




def run_projects():
    for project_name in os.listdir(projects_root):
        project_dir = os.path.join(projects_root, project_name)
        if not os.path.isdir(project_dir):
            continue
        else:
            run_project(project_dir)



# 这个脚本
xserver_start_projects_script = """#!/usr/bin/python
import sys
from xserver.utils.docker_utils import print_docker_status
from xserver.server.project import run_projects
if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] == 'start':
        run_projects()
    else:
        print_docker_status()
"""


def install_xserver_started():
    script_filepath = '/etc/init.d/started'
    write_file(script_filepath, xserver_start_projects_script)
    run_commands('chmod +x %s' % script_filepath)

    run_commands('export LC_ALL="en_US.UTF-8"')
    run_commands('update-rc.d started defaults 95') # 启动各项目容器的脚本