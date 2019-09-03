# coding: utf8
import sys
import os
import subprocess
import time

def run_commands(commands, sleep=0):
    for command in commands.split('\n'):
        command = command.strip()
        if command.startswith('#'): continue # just comment
        if not command: continue
        subprocess.call(command, shell=True)
        if sleep: time.sleep(sleep)


CSI="\x1B["
RED = CSI+"31;40m"
GREEN = CSI+'32;40m'
RESET =CSI+"m"

def print_color(color, strings):
    if color == 'green':
        print GREEN + strings + RESET
    elif color == 'red':
        print RED + strings + RESET
    else:
        print strings



def install_packages_from_config_file(filepath):
    with open(filepath) as f:
        install_type = 'apt'
        install_types = ['apt', 'pip', 'shell']
        for line in f.readlines():
            line_content = line.strip()
            if line_content.startswith('#'): # 注释
                line_mark = line_content.strip('#').lower()
                if line_mark in install_types:
                    install_type = line_mark # 切换安装方式
                continue
            else: # 开始正式安装
                if install_type == 'apt':
                    command = "apt-get install -y %s" % line_content
                elif install_type == 'pip':
                    command = "pip install %s" % line_content
                elif install_type == 'shell': # run raw command
                    command = line_content
                else:
                    command = ''
                if command:
                    print_color('green', command)
                    run_commands(command)




if __name__ == '__main__':
    packages_filepath = sys.argv[1]
    if not os.path.isfile(packages_filepath):
        print '%s is not found' % packages_filepath
    else:
        install_packages_from_config_file(packages_filepath)
