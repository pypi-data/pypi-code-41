# coding: utf8
from __future__ import absolute_import
# 主要是守护 docker 上各个镜像、container 的存活

import time, os, logging
from xserver.utils.docker_utils import get_containers, update_docker_ips
from xserver.utils.command import run_commands
from xserver.server.project import run_projects, run_project, projects_root
from xserver.utils.cronjob import create_py_command_cronjob, create_cronjob

#logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


logger_handler = logging.FileHandler('/var/log/lived.log')
logger_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logger_handler.setFormatter(formatter)

def install_logger_handler():
    logger.addHandler(logger_handler)


def keep_projects_live():
    install_logger_handler()

    containers = get_containers()
    container_names = containers.keys()

    containers_to_remove = [] # 需要删除的容器, 其实是先删除，后重启
    projects_to_restart = [] # 需要重启的容器

    for container_name in os.listdir(projects_root):
        project_name = container_name # project_name & container_name 是等价的
        container = containers.get(container_name)
        if not container:
            projects_to_restart.append(project_name)
        else:
            if not container.get('is_live') and not container_name.endswith('_failed'): # 停止了的 container
                projects_to_restart.append(project_name)
                containers_to_remove.append(container_name)

    # 先移除已经异常状态的 containers
    containers_to_remove = list(set(containers_to_remove))
    for container_name in containers_to_remove:
        try:
            try: run_commands('docker logs -t %s >> /var/log/docker_errors.log' % container_name)
            except: pass
            # as backup for debug
            failed_container_name = '%s_failed' % container_name
            try: run_commands('docker rm -f %s' % failed_container_name)
            except: pass
            try: run_commands('docker rename %s %s' % (container_name, failed_container_name))
            except: pass
            try: run_commands('docker rm -f %s' % container_name)
            except: pass
            logger.info('docker container: %s is removed' % container_name)
        except:
            logger.info('docker container: %s failed to remove' % container_name)

    # 启动需要更新的 project folder, 会自动启动缺失的 container

    projects_to_restart = list(set(projects_to_restart))
    for project_name in  projects_to_restart:
        run_project(project_name)
        logger.info("%s started" % project_name)

    # 记录一下 docker 各个容器的ip 情况
    update_docker_ips()

    logger.info('keep containers live, done')


def keep_projects_live_by_loop(per_minutes=10):
    run_projects() # 先启动所有项目先

    while True:
        time.sleep(30) # 等待/etc/init.d/started 启动成功了再说
        try:
            keep_projects_live()
        except:
            logger.error('run keep_projects_live failed')
        time.sleep(per_minutes*60) # per 10 minutes



def install_keep_live_cronjob():
    command = '/usr/local/bin/xserver keep_live'
    cronjob = create_cronjob(command, minutes=2, write=True)
    #py_command = 'from xserver.server.keep_live import keep_projects_live; keep_projects_live()'
    #cronjob = create_py_command_cronjob(py_command, minutes=2, write=True)
    return cronjob