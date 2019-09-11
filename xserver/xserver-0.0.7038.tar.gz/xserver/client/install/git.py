#coding: utf8
from __future__ import absolute_import
from xserver.client.utils.fab import run, put_file, put_file_content
from xserver.utils.path import get_home_path, make_sure_path, write_file
from xserver.helper.private_key import create_private_public_keys_for_ssh
import os

ssh_config_content = """StrictHostKeyChecking no
UserKnownHostsFile /dev/null"""

def install_git(user_name='server', user_email='server@domain.com'):
    # 安装 git & 配置基础的环境（用于未来的git pull 以作部署用）
    run('apt-get install -y git-core')
    run('git config --global user.name "%s"' % user_name)
    run('git config --global user.email "%s"' % user_email)

    put_file_content(ssh_config_content, '/root/.ssh/config') # 这样可以避免连接时询问known_hosts


    # install private key too
    install_git_private_key()



def create_local_git_keys(force=False):
    home_path = get_home_path()
    private_key_filepath = os.path.join(home_path, '.ssh/xserver_git_id_rsa')
    public_key_filepath = os.path.join(home_path, '.ssh/xserver_git_id_rsa.pub')
    make_sure_path(private_key_filepath)
    if not force and os.path.isfile(private_key_filepath) and os.path.isfile(public_key_filepath):
        pass
    else:
        private_key, public_key = create_private_public_keys_for_ssh()
        write_file(private_key_filepath, private_key)
        write_file(public_key_filepath, public_key)
    return private_key_filepath


def install_git_private_key(force_create_private_key=False):
    # 在 服务器 的 HOST 中部署私钥, 这样可以远程 pull git repo 回来
    private_key_filepath = create_local_git_keys(force=force_create_private_key)
    put_file(private_key_filepath, '/root/.ssh/id_rsa')
    run('chmod 600 /root/.ssh/id_rsa')
