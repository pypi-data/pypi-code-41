#coding: utf8
from __future__ import absolute_import
from xserver.utils.functional import curry
from xserver.docker_image.utils import build_docker_image
from xserver.docker_image.templates.utils import build_common_image


build_demo = curry(build_common_image, image_name='xserver_demo_app', version='0.1')

build_pyweb = curry(build_common_image, image_name='pyweb', version='2019')

build_farbox_bucket = curry(build_common_image, image_name='farbox_bucket', version='x')

build_mongodb = curry(build_common_image, image_name='mongodb', version='3.6.5', version_in_docker_file='3.6.5')


build_ipfs = curry(build_common_image, image_name='ipfs', version='0.4.18', version_in_docker_file='0.4.18')

build_supervisor = curry(build_common_image, image_name='supervisor', version='2019')


#build_common_image(image_name='supervisor', version='18.04', version_in_docker_file='16.04')

######### pyubuntu starts #########

py_ubuntu_docker_file_script = """FROM ubuntu:%s

RUN apt-get update
RUN apt-get install -y apt-utils
RUN apt-get install -y wget python-dev python-pip nano
RUN pip install --upgrade pip

RUN mkdir -p /etc/resolvconf/resolv.conf.d
RUN echo -e "nameserver 8.8.8.8\\nnameserver 8.8.4.4" > /etc/resolv.conf
RUN echo -e "nameserver 8.8.8.8\\nnameserver 8.8.4.4" > /etc/resolvconf/resolv.conf.d/tail"""

def build_pyubuntu(version='16.04', username=None):
    ubuntu_version = version
    docker_file_content = py_ubuntu_docker_file_script % ubuntu_version
    build_docker_image(
        username = username,
        image_name = 'pyubuntu',
        image_version = ubuntu_version,
        docker_file_content = docker_file_content,
    )

######### pyubuntu ends #########