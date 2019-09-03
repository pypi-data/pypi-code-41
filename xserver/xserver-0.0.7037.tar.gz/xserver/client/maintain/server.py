#coding: utf8
from __future__ import absolute_import
from xserver.client.utils.fab import *
from xserver.client.utils.remote_docker_utils import run_in_docker, show_docker_status, copy_file_and_run_it_in_docker
import re


# 一些常见的后续更新命令, container==project_name
# project 主要就是 main_project


########### basic starts ############
def docker_status():
    show_docker_status()


def just_update_app_repo(project):
    app = project.rsplit('_',1)[0]
    #run('cd /app/%s && git pull' % app)
    run('if [ -f /app/%s ]; then cd /app/%s && git pull; fi'% (app, app) )

just_update = just_update_app_repo


def update_pid(project, pid_name='web_server'):
    just_update_app_repo(project)
    run_in_docker(project, 'kill -HUP `cat /tmp/%s.pid`'%pid_name)
    run_in_docker(project, 'supervisorctl status')


def restart_service(project, service):
    run_in_docker(project, 'service %s restart' % service)
    run_in_docker(project, 'service %s status' % service)




def run_web_py_script(project, cmd):
    # like run_in_docker(project, 'python /mt/web/app/before_startup.py')
    cmd = cmd.strip()
    if '.py' not in cmd:
        cmd += '.py'
    cmd = 'python /mt/web/app/%s' % cmd
    run_in_docker(project, cmd)



def upload_static_file(project, filepath):
    if not os.path.isfile(filepath):
        print('cant find %s' % filepath)
        return
    filename = os.path.split(filepath)[-1]
    filepath_on_server = '/static/%s/%s' % (project, filename)
    put_file(filepath, filepath_on_server)



def delete_static_file(project, filename):
    filepath_on_server = '/static/%s/%s' % (project, filename)
    run('rm %s' % filepath_on_server)


########### basic ends ###############



############ supervisor starts #############

def supervisor_status(project):
    run_in_docker(project, 'supervisorctl status')


def restart_supervisor(project):
    # 所有的 supervisor 的服务重启
    just_update_app_repo(project)
    run_in_docker(project, 'supervisorctl restart all')
    run_in_docker(project, 'supervisorctl status')

restart_all = restart_supervisor


def update_supervisor(project):
    # 如果有新增的 supervisor 进程，可以用这个
    run_in_docker(project, 'supervisorctl reread')
    run_in_docker(project, 'supervisorctl update') # 如果缺失的 job，会添加
    run_in_docker(project, 'supervisorctl status')



def restart_supervisor_services(project, service=None, *services):
    # 重启 supervisor 管理的进程
    # 在console handle的时候，可以直接 update_xxx 来实现这个调用
    services = list(services)
    if service:
        services.append(service)
    just_update_app_repo(project)
    print '\n'*8
    for service in services:
        run_in_docker(project, 'supervisorctl restart %s' % service)
    if services:
        run_in_docker(project, 'supervisorctl status')


############ supervisor ends #############




########## nginx starts ###########

def check_nginx(project):
    run_in_docker(project, 'if [-f /check_nginx]; then /check_nginx; fi')

def update_nginx(project):
    # nginx 的配置重载
    check_nginx(project)
    just_update_app_repo(project) # 可能有 lua 脚本的更新

    run_in_docker(project, '/usr/nginx/sbin/nginx -s reload')


def restart_nginx(project):
    # /var/run/nginx.pid
    # 小心操作，重启 nginx，可能需要 reset-cache 的需要，比如 ssl 的 cache
    check_nginx(project)

    just_update_app_repo(project) # 可能有 lua 脚本的更新

    # 可能有情况，会导致  /var/run/nginx.pid 内没有进程信息……
    #run_in_docker(project, """if [[ -z `cat /var/run/nginx.pid | tr -d ' '` ]] ; then echo `ps aux | grep nginx | grep master | awk '{print $2}'` > /var/run/nginx.pid;  fi;""")

    run_in_docker(project, '/etc/init.d/nginx restart')
    #run_in_docker(project, '/usr/nginx/sbin/nginx -s quit')
    #run_in_docker(project, '/etc/init.d/nginx start')

######### nginx ends ##########



def update_web(project):
    # web 服务的（不中断）更新
    update_pid(project, pid_name='web_server')


def restart_cache(project):
    # memcache 的重启
    restart_service(project, 'memecached')









###########################


def main():
    pass