#coding: utf8
from __future__ import absolute_import
from fabric.api import run

def install_docker():
    try:
        run('apt-get remove -y docker docker-engine docker.io')
    except:
        pass
    run('mkdir -p /etc/systemd/system/containerd.service.d')
    run('rm -f /etc/systemd/system/containerd.service.d/override.conf')
    run('echo "[Service]" >> /etc/systemd/system/containerd.service.d/override.conf')
    run('echo "ExecStartPre=" >> /etc/systemd/system/containerd.service.d/override.conf')
    run('apt-get update') # --fix-missing
    run('apt-get install  apt-transport-https  ca-certificates   curl   software-properties-common -y')
    run('curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -')
    run('add-apt-repository    "deb [arch=amd64] https://download.docker.com/linux/ubuntu   $(lsb_release -cs)   stable"')
    run('apt-get update')
    run('apt-get install docker-ce -y')