#coding: utf8
from __future__ import absolute_import
import os
import json
import base64
from xserver.utils import string_types, unicode, to_bytes
from xserver.utils.path import get_relative_path, get_file_list, make_sure_path
import importlib


#deploy_dir = os.path.abspath(os.path.dirname(__file__))


def dump_deploy_dir(deploy_dir, ignored_filenames=()):
    # 将一个 deploy_dir 内的文件, 压缩为一个 py 文件, 并存于 deploy_dir 下的 files.py 中
    files_data = {}
    filepaths = get_file_list(deploy_dir)
    py_filepath = os.path.join(deploy_dir, 'files.py')
    ignored_filenames = ['_dump.py', 'deploy.py', 'readme.txt', '__init__.py', 'files.py'] + list(ignored_filenames)
    for filepath in filepaths:
        relative_path = get_relative_path(filepath, root=deploy_dir)
        if relative_path in ignored_filenames:
            continue
        if relative_path.endswith('.pyc') or relative_path.endswith('.pyo'):
            continue
        if not os.path.isfile(filepath):
            continue
        with open(filepath, 'rb') as f:
            file_content = f.read()
        files_data[relative_path] = base64.b64encode(file_content)
        files_data_s = json.dumps(files_data)
        py_file_content = 'files_data="""%s"""' % files_data_s
        with open(py_filepath, 'wb') as f:
            f.write(py_file_content)



def deploy_project_dir(files_data, project_name, memcache=None, cpu=None, mem=None, cpus=None):
    # try module first,  xx or xx.xx.xx
    if files_data == 'none':
        # 相当于创建了一个空的，然后通过其它方式进行填充配置文件
        files_data = {}

    if len(files_data) <= 50 and '/' not in files_data:
        module_name = files_data
        try:
            # hit deploy_files under xserver first
            d_module = importlib.import_module('xserver.deploy_files.%s.files' % module_name)
            files_data = d_module.files_data
        except:
            try:
                d_module = importlib.import_module('%s.deploy.files' % module_name)
                files_data = d_module.files_data
            except:
                d_module = importlib.import_module('%s.files' % module_name)
                files_data = d_module.files_data
                # raise error if happen

    # then tray filepath
    if files_data.startswith('/'):
        # load data from filepath or dir (like work folder)
        if os.path.isdir(files_data):
            data_filepath = os.path.join(files_data, 'files.py')
            if not os.path.isfile(data_filepath):
                data_filepath = os.path.join(files_data, 'deploy/files.py')
        else:
            data_filepath = files_data
        if os.path.isfile(data_filepath):
            #with open(data_filepath, 'rb') as f:
                #raw_files_data_file_content = f.read()
            try:
                exec_data = {}
                execfile(data_filepath, exec_data)
                files_data = exec_data.get('files_data')
            except:
                pass

    # now, check data

    # 校验
    if not isinstance(files_data, dict):
        try:
            files_data = json.loads(files_data)
            if not isinstance(files_data, dict):
                print('deploy_project_dir error')
                return
        except:
            print('deploy_project_dir error')
            return

    files_data = {k:base64.b64decode(v) for k,v in files_data.items()}
    project_name = project_name.strip()
    if project_name.startswith('/'):
        project_dir = project_name
    else:
        project_dir = '/home/run/%s' % project_name
    make_sure_path(project_dir, is_dir=True)
    for relative_path, file_content in files_data.items():
        # max mem for memcache
        if memcache and 'memcached.conf' in relative_path:
            memcache = memcache.lower().replace('mb', '').strip()
            memcache = int(memcache)
            file_content = file_content.replace('-m 1024', '-m %s'%memcache)

        filepath = os.path.join(project_dir, relative_path)
        make_sure_path(filepath)
        with open(filepath, 'wb') as f:
            file_content = to_bytes(file_content)
            f.write(file_content)

    # docker 容器的资源限制
    docker_limit = ''
    if cpu:
        # cat /sys/fs/cgroup/cpu/docker/cpu.shares -> 1024
        # 是相对于 1024 total value 的 weight， 如果 <=1， 权重重新计算成绝对值
        # 如果没有设定，默认值是  1024， 是相对多个容器而言各自产生的比重
        try:
            cpu_float = float(cpu)
            if cpu_float <= 1:
                cpu = str(int(1024*cpu_float))
        except:
            pass
        docker_limit += ' --cpu-shares=%s' % cpu
    if cpus: # 可用核数(资源），并不严格物理性控制，其实相当于百分比, 2/4, 就是相当于 50%
        docker_limit += ' --cpus=%s' % cpus
    if mem:
        docker_limit += ' -m %s' % mem
    docker_limit = docker_limit.strip()
    if docker_limit:
        docker_container_env_filepath = '/home/env/%s' % project_name
        make_sure_path(docker_container_env_filepath)
        with open(docker_container_env_filepath, 'wb') as f:
            f.write(docker_limit)


def deploy_project_from_local(remote_ip, local_project_dir, project_name=''):
    from xserver.client.utils.fab import put_file, make_env, run
    dump_deploy_dir(local_project_dir)
    make_env(remote_ip)
    put_file('%s/files.py'%local_project_dir, '/tmp/py_project.py')
    if project_name:
        run('xserver_package deploy /tmp/py_project.py %s' % project_name)
