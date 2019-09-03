#coding: utf8
from __future__ import absolute_import
from xserver.utils.command import run_commands
from xserver.utils.path import make_sure_path, read_file, write_file
from xserver.utils.cli_color import print_with_color
from xserver.utils.docker_utils import get_default_docker_username
import os, importlib


tmp_docker_context_folder = '/tmp/docker_context'


def build_docker_image(image_name, image_version, docker_file_path=None, docker_file_content=None, username=None, **kwargs):
    # image_name like  username/real_name
    if not docker_file_path and not docker_file_content:
        return

    if '/' not in image_name:
        # 用 username 自动补全 image_name
        if not username:
            username = get_default_docker_username()
        if username:
            image_name = '%s/%s' % (username, image_name)

    make_sure_path(tmp_docker_context_folder, is_dir=True)
    if not docker_file_path:
        docker_file_path = os.path.join(tmp_docker_context_folder, 'Dockerfile')
        write_file(docker_file_path, docker_file_content)
    docker_context_folder = os.path.dirname(docker_file_path)
    docker_file_name = os.path.split(docker_file_path)[-1]
    docker_image_full_name = '%s:%s' % (image_name, image_version)
    build_args_list = []
    for k, v in kwargs.items():
        build_args_list.append('%s=%s' % (k,v))
    build_args = ' '.join(build_args_list)
    if build_args:
        build_args = ' --build-arg %s ' % build_args

    os.chdir(docker_context_folder)
    build_command = 'docker build -f %s -t %s %s %s' % (docker_file_name, docker_image_full_name, build_args, docker_context_folder)
    print_with_color(build_command, 'green')
    run_commands(build_command)

    run_commands('docker tag %s:%s %s:latest' % (image_name, image_version, image_name))


def update_docker_image(image_name, old_version=None, new_version=None, cmds=None):
    default_username = get_default_docker_username()
    if '/' not in image_name:
        image_name = '%s/%s' % (default_username, image_name)
    if ':' in image_name:
        image_name, old_version = image_name.split(':', 1)
    if not new_version:
        new_version = old_version
    if not new_version and not old_version:
        return print_with_color('need set version', 'red')

    raw_full_new_image_name = '%s:%s' % (image_name, new_version)

    to_replace = False
    if new_version == old_version:
        to_replace = True
        new_version = '%s_tmp' % new_version
        print_with_color('old version and new version are same, will be replaced', 'red')
    if old_version:
        full_old_image_name = '%s:%s' % (image_name, old_version)
    else:
        full_old_image_name = image_name
    full_new_image_name = '%s:%s' % (image_name, new_version)

    if not isinstance(cmds, (list, tuple)):
        cmds = []

    for cmd in cmds:
        print_with_color(cmd, 'cyan')

    docker_file_content_list=  ['FROM %s'%full_old_image_name] + list(cmds)
    docker_file_content = '\n'.join(docker_file_content_list)
    build_docker_image(image_name, image_version=new_version, docker_file_content=docker_file_content)

    if to_replace:
        #run_commands('docker rmi %s' % full_old_image_name) # remove old tag first
        run_commands('docker tag %s %s' % (full_new_image_name, full_old_image_name)) # tag new one
        run_commands('docker rmi %s' % full_new_image_name)

    #run_commands('docker tag %s %s:latest' % (raw_full_new_image_name, image_name))


def load_files_data(files_data):
    docker_file_content = files_data.pop('Dockerfile', '')
    for filename, file_content in files_data.items():
        tmp_filepath = os.path.join(tmp_docker_context_folder, filename)
        write_file(tmp_filepath, file_content)
    return docker_file_content


