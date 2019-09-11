#coding: utf8
from __future__ import absolute_import
import importlib
from xserver.docker_image.utils import build_docker_image, load_files_data
from xserver.utils.cli_color import print_with_color
import os


def build_common_image(image_name, version='default', version_in_docker_file=None, username=None):
    try:
        # 直接传入一个 DockerFile 进行构建
        if os.path.isfile(image_name) and '/' in image_name:
            docker_file_path = image_name
            image_name = os.path.split(docker_file_path)[-1].split('.')[0]
            build_docker_image(
                username=username,
                image_name=image_name,
                image_version=version,
                docker_file_path=docker_file_path
            )
            return # done
    except:
        pass

    try:
        m = importlib.import_module('xserver.docker_image.files.%s' % image_name)
        files_data = m.files_data
    except ImportError:
        print_with_color('import files.%s error'%image_name, color='red')
        return
    docker_file_content = load_files_data(files_data)
    if version_in_docker_file: # 在 docker_file 中需要替换掉的
        docker_file_content = docker_file_content.replace(version_in_docker_file, version)
    build_docker_image(
        username = username,
        image_name = image_name,
        image_version = version,
        docker_file_content = docker_file_content,
    )