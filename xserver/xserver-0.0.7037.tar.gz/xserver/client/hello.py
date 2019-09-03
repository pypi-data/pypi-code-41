#coding: utf8
from __future__ import absolute_import
from xserver.client.utils.fab import disconnect_all
from xserver.client.init.ssh import re_config_ssh
from xserver.client.init.deploy_env import create_mini_env
from xserver.client.install.docker import install_docker
from xserver.client.install.git import install_git
from xserver.client.install.xserver import install_xserver

def hello_server(ip, user=None, password=None):
    disconnect_all()
    
    # step 1, init ssh config
    re_config_ssh(ip, user=user, password=password)

    # step 2, basic server env for HOST
    create_mini_env()

    # step 3, install HOST softwares
    install_docker()
    install_git()

    install_xserver()


