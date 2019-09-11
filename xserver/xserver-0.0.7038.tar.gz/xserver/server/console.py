#coding: utf8
from __future__ import absolute_import
from xserver.server.project import run_projects, run_project, install_xserver_started
from xserver.server.keep_live import keep_projects_live, install_keep_live_cronjob
from xserver.utils.docker_utils import print_docker_status
from xserver.utils.console_utils import get_args_from_console, get_first_arg_from_console
from xserver.utils.cli_color import print_with_color
from xserver.utils.command import run_commands
import os, sys

# 无参数传入的运行方式
# xserver start, install_start, live, install_live
# xserver start <project_name>
# xserver stop <project_name>
# xserver live_log



def main():
    raw_args = sys.argv[2:]
    kwargs, args = get_args_from_console(raw_args)
    action = get_first_arg_from_console()
    if not kwargs: # 没有特别参数传入, 只是当前的运行逻辑
        if action in ['start', 'started']:
            if args:
                for project_name in args:
                    run_project(project_name)
                    print_with_color('start %s'%project_name, 'green')
            else:
                run_projects()
        elif action == 'stop' and args: # remove project too
            project_to_stop = args[0]
            project_dir = '/home/run/%s' % project_to_stop
            if os.path.isdir(project_dir) and project_dir and project_dir != '/' and '.' not in project_dir:
                run_commands('rm -rf %s'%project_dir)
            try: run_commands('docker rm -f %s' % project_to_stop)
            except: pass
        elif action in ['install_start', 'install_started']:
            install_xserver_started()
        elif action in ['live', 'keep_live']:
            keep_projects_live()
        elif action == 'install_live':
            install_keep_live_cronjob() # 每 2 分钟会执行一次
            run_commands('crontab -l')
        elif action == 'live_log':
            run_commands('tail /var/log/lived.log -n 20')
        else:
            print_docker_status()
    else: # 有参数传入的情况
        pass


if __name__ == '__main__':
    main()

