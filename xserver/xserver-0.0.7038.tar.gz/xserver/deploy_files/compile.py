# coding: utf8
import os
from xserver.helper.package_utils import dump_deploy_dir

def dump_deploy_files_dirs():
    deploy_files_folder = os.path.dirname(os.path.abspath(__file__))
    for sub_name in os.listdir(deploy_files_folder):
        project_template_dir = os.path.join(deploy_files_folder, sub_name)
        if os.path.isdir(project_template_dir):
            dump_deploy_dir(project_template_dir)


if __name__ == '__main__':
    dump_deploy_files_dirs()

