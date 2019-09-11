# Copyright (C) 2019 Erhu Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import shutil

from dkrs.log import log, warning, error
from dkrs.system import os_popen, os_system_tip, get_user_input, os_system


class Git:

    def __init__(self):
        pass

    @staticmethod
    def is_git_dir(workspace):
        """
        检查此目录是否是一个有效 git 目录
        """
        return os.path.exists('{}/.git'.format(workspace))

    @staticmethod
    def get_repo_name_from_url(repo):
        """
        从 git 地址中获得克隆时目录的位置
        :param repo: git@gitlab.alibaba-inc.com:amap-scm-android/bundle_template.git
        :return bundle_template
        """
        repo = repo.strip()
        if repo and repo != '':
            return repo.split('/')[-1].split('.')[0]
        else:
            return None

    @staticmethod
    def get_repo_name_from_workspace(workspace):
        """
        从 仓库目录 中获得克隆时目录的位置
        """
        if os.path.exists(workspace):
            os.chdir(workspace)
            return Git.get_repo_name_from_url(os_popen('git config --get remote.origin.url'))
        else:
            return None

    @property
    def config(self):
        return os_popen('git config --get user.name').strip(), os_popen('git config --get user.email').strip()

    @staticmethod
    def is_shallow_workspace(workspace):
        """
        repo_path 所在仓库是否是 浅克隆仓库
        """
        return os.path.exists('{}/.git/shallow'.format(workspace))

    @property
    def version(self):
        """
        返回本机 git 版本
        """
        version_info = os_popen('git version')
        p = re.compile(r'\d\.\d+\.\d+')
        versions = p.findall(version_info)
        return versions[0] if len(versions) > 0 else None

    @staticmethod
    def do_fetch():
        return os_system('git fetch', with_output=False)

    @staticmethod
    def do_pull():
        return os_system('git pull', with_output=False)

    @staticmethod
    def is_branch_exists(branch, remote='origin'):
        """
        查询 branch 分支是否存在
        """
        result = os_popen('git branch -r')
        result = result.split('\n')
        for item in result:
            if '{}/{}'.format(remote, branch) == item.strip():
                return True
        return False

    @staticmethod
    def is_branch_merged_into(origin_branch, target_branch, remote='origin'):
        """
        检查 origin_branch 是否已经合并到 target_branch
        """
        # 输出有哪些分支 merge 进了 target 分支
        result = os_popen('git branch -r --merged {}/{}'.format(remote, target_branch))
        result = result.split('\n')
        for item in result:
            if '{}/{}'.format(remote, origin_branch) == item.strip():
                return True
        return False

    @staticmethod
    def get_current_branch(workspace):
        """
        获取当前目录下，Git 仓库的基本信息
        """
        head_file = '{}/.git/HEAD'.format(workspace)
        if not os.path.exists(head_file):
            error("{} 文件不存在，获取 Git 分支失败".format(head_file))
            exit(1)

        with open(head_file, 'rt') as f:
            data = f.read().replace('\n', '')
            return data.split('refs/heads/')[-1]

    @staticmethod
    def checkout_force(branch):
        """强制切换分支"""
        return os_system_tip('git checkout -f {}'.format(branch), "切换到 {} 分支".format(branch))

    @staticmethod
    def clone(repo, branch, deep_clone=True):
        if deep_clone:
            os.system("git clone -b {} {}".format(branch, repo))
        else:
            Git.clone_shallow(repo, branch)

    @staticmethod
    def clone_to_dir(repo, branch, dir_name):
        os.system("git clone -b {} {} {}".format(branch, repo, dir_name))

    @staticmethod
    def clone_shallow(repo, branch):
        os.system("git clone --depth 1 -b {} {}".format(branch, repo))

    @staticmethod
    def clone_shallow_to_dir(repo, branch, dir_name):
        os.system("git clone --depth 1 -b {} {} {}".format(branch, repo, dir_name))

    @staticmethod
    def clone2(workspace, repo, branch, deep_clone=True):
        """
        克隆仓库，如果已存在，则切换分支，更新代码
        """
        repo_dir = Git.get_repo_name_from_url(repo)
        repo_path = '{}/{}'.format(workspace, repo_dir)

        os.chdir(workspace)

        if not os.path.exists(repo_path):
            Git.clone(repo, branch, deep_clone)
        else:
            Git.update_repo(repo_path, repo, branch, deep_clone)

    @staticmethod
    def update_repo(repo_path, repo_url, branch, deep_clone=True):
        # 不是有效的 git 目录
        if not Git.is_git_dir(repo_path):
            warning('{} 不是有效的 git 目录(没有 .git 文件)'.format(repo_path))
            choice = get_user_input('要删除它并重新下载吗？y/n', ['y', 'n'], default='y')
            if not choice or choice not in ['y', 'Y']:
                return
            os.chdir('{}/../'.format(repo_path))
            # 删除原目录
            shutil.rmtree(repo_path)
            # 重新克隆
            Git.clone(repo_url, branch, deep_clone=deep_clone)

        else:
            # 是有效的 git 目录
            # 检查是否是浅克隆
            if Git.is_shallow_workspace(repo_path):  # 浅克隆，检查是否下载全分支
                # 下载全分支
                if deep_clone:
                    os.chdir(repo_path)
                    os_system_tip("git remote set-branches origin '*'", with_output=False)
                    os_system_tip('git fetch', with_output=False)
                    if not os_system_tip('git checkout {}'.format(branch), "切换到 {} 分支".format(branch),
                                         with_output=True):
                        log("退出")
                        exit(1)
                    if not os_system_tip('git pull', "下载 {}".format(branch), with_output=True):
                        log("退出")
                        exit(1)

                # 下载单个分支
                else:
                    os.chdir(repo_path)
                    os_system_tip("git remote set-branches origin '{}'".format(branch), with_output=False)
                    os_system_tip('git fetch --depth 1 origin {}'.format(branch), with_output=False)
                    if not os_system_tip('git checkout {}'.format(branch), "切换到 {} 分支".format(branch),
                                         with_output=True):
                        log("退出")
                        exit(1)
                    if not os_system_tip('git pull', "下载 {}".format(branch), with_output=True):
                        log("退出")
                        exit(1)
            else:
                # 非浅克隆，只能下载全分支
                os.chdir(repo_path)
                os_system_tip('git fetch', with_output=False)
                if not os_system_tip('git checkout {}'.format(branch), "切换到 {} 分支".format(branch), with_output=True):
                    log("退出")
                    exit(1)
                if not os_system_tip('git pull', "下载 {}".format(branch), with_output=True):
                    log("退出")
                    exit(1)
