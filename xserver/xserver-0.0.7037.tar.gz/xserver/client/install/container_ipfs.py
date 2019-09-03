#coding: utf8
from __future__ import absolute_import
from xserver.client.utils.fab import run, put_file_content, env
import json
import os
import re

# project related




def install_ipfs_server_container(project_name='ipfs_server', cpu=0.5, mem='3g',
                                    port=6001, max_storage=None, peer_id=None, private_key=None, ip=None, ipv6=None, bootstrap=None):
    # max_storage='2TB'
    run('xserver_package deploy xserver.deploy_files.ipfs %s cpu=%s mem=%s' % (project_name, cpu, mem))

    ipfs_run_folder = '/home/run/%s' % project_name
    ipfs_configs_folder = os.path.join(ipfs_run_folder, 'configs')
    run('mkdir -p %s' % ipfs_configs_folder)



    # supervisor 中 process 的名称修改
    supervisord_config_filepath = os.path.join(ipfs_configs_folder, 'supervisord.conf')
    run('xserver_package replace %s [program:ipfs] [program:%s]' % (supervisord_config_filepath, project_name))

    # run.sh 中端口的对应
    port = str(port)
    if port != '6001':
        run_sh_filepath = os.path.join(ipfs_run_folder, 'run.sh')
        run('xserver_package replace %s 6001:6001 %s:%s' % (run_sh_filepath, port, port))


    # 对应 ipfs.json 这个config，以让服务器上自动修正
    ipfs_server_config_filepath = '%s/ipfs.json' % ipfs_configs_folder
    ipfs_server_config = {'port': port}
    if max_storage:
        ipfs_server_config['max_storage'] = max_storage
    if peer_id and private_key:
        ipfs_server_config['peer_id'] = peer_id
        ipfs_server_config['private_key'] = private_key

    if bootstrap:
        # 设置一个主节点
        if not isinstance(bootstrap, (list, tuple)):
            bootstrap = [bootstrap.strip()]
        ipfs_server_config['bootstrap'] = bootstrap

    if not ip:
        ip_in_env = env.host_string
        if re.match('\d+\.\d+\.\d+\.\d+$', ip_in_env):
            ip = ip_in_env
            print('got ip %s from fabric env' % ip)

    if ip:
        ipfs_server_config['ip'] = ip
    if ipv6:
        ipfs_server_config['ipv6'] = ipv6
    ipfs_server_config_content = json.dumps(ipfs_server_config, indent=4)
    put_file_content(ipfs_server_config_content, ipfs_server_config_filepath)


    # 启动这个项目
    run('xserver start %s' % project_name)

