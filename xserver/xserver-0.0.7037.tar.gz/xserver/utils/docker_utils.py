#coding: utf8
from __future__ import absolute_import
import os
from xserver.utils.command import run_commands
from xserver.utils.cli_color import print_with_color
import re

def docker_cmd_to_py_data(cmd, fields):
    joiner = ' ; '
    keys = [field.lower() for field in fields]
    fields = ['{{.%s}}'%field for field in fields]
    format_cmd = ' --format "%s"' % joiner.join(fields)
    cmd = '%s %s' % (cmd, format_cmd)
    fp = os.popen(cmd)
    result_list = fp.read().strip().split('\n')
    fp.close()
    datas = {}
    for line in result_list:
        line_parts = line.strip().strip(joiner.strip()).split(joiner)
        line_parts = [i.strip() for i in line_parts]
        if len(line_parts) == len(keys):
            one_data = dict(zip(keys, line_parts))
            key_value = line_parts[0] # first one will be the main key
            datas[key_value] = one_data
    return datas



def get_containers():
    containers = docker_cmd_to_py_data('docker ps -a', ['Names', 'ID', 'Image', 'Status'])
    for name, container in containers.items():
        container_status = container['status']
        is_live = container_status.lower().startswith('up ')
        container['is_live'] = is_live
    return containers



def get_images():
    # {'image_id': {id, tag, repository}}
    images = docker_cmd_to_py_data('docker images', ['ID', 'Repository', 'Tag'])
    return images


def get_image_names(with_tag=True):
    # ['xxx/xxx'] or ['xxx/xxxx:xxx']
    images = get_images()
    image_names = []
    for image in images.values():
        image_name = image['repository']
        image_tag = image['tag']
        if with_tag:
            name = '%s:%s' % (image_name, image_tag)
        else:
            name = image_name
        image_names.append(name)
    return image_names



def has_image(image_name):
    # 本地是否已经存在镜像了
    image_names = get_image_names(with_tag=True)
    if ':' in image_name:
        check_name = image_name
    else:
        check_name = '%s:latest' % image_name
    return check_name in image_names



def get_docker_login_username():
    fp = os.popen('docker info')
    result = fp.read().strip() or ''
    fp.close()
    re_c = re.search('Username: ([a-z0-9]+)', result, flags=re.I)
    if re_c:
        username = re_c.group(1)
        username = username.strip()
        return username
    return ''

def get_default_docker_username():
    docker_login_username = get_docker_login_username()
    if docker_login_username:
        return docker_login_username
    usernames = {}
    image_names = get_image_names(with_tag=False)
    for image_name in image_names:
        if '/' in image_name:
            username = image_name.split('/')[0]
            usernames[username] = usernames.get('username', 0) + 1
    count_usernames = [(v, k) for k,v in usernames.items()]
    count_usernames.sort()
    if count_usernames:
        return count_usernames[0][1]



def update_docker_ips():
    command = "mkdir -p /log/docker; docker ps -q | xargs docker inspect --format '{{ .Name }} {{ .NetworkSettings.IPAddress }}' > /log/docker/ips.txt"
    run_commands(command)



def print_docker_status():
    image_names = get_image_names(with_tag=True)
    print_with_color('Docker Images Are: \n', color='cyan')
    print_with_color('%s'% ' , '.join(image_names), color='green')
    print('\n'*3)

    containers = get_containers()
    for container_name, container in containers.items():
        if container.get('is_live'):
            print_with_color('%s is on running' % container_name, color='green')
        else:
            print_with_color('%s is not on running' % container_name, color='red')



def clear_device_mapper():
    containers = get_containers()
    container_ids = [v['id'][:12] for v in containers.values()]
    mnt_path = '/var/lib/docker/devicemapper/mnt'
    sub_names = os.listdir(mnt_path)
    sub_paths_to_remove = []
    for name in sub_names:
        if name[:12] in container_ids:
            continue
        else:
            sub_paths_to_remove.append(os.path.join(mnt_path, name))
    for sub_path in sub_paths_to_remove:
        os.popen('rm -rf %s'%sub_path)
