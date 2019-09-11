#coding: utf8
from __future__ import absolute_import
from xserver.server_status.status.status import get_system_status
from xserver.utils.path import write_file
from xserver.utils.command import run_commands, get_matched_ps
from xserver.utils.cli_color import print_with_color
from xserver.utils.cronjob import create_py_command_cronjob, create_cronjob
from farbox_bucket.client.project import  set_project_node, get_project_bucket
from farbox_bucket.client.action import create_record_for_project, create_bucket_for_project, update_bucket_configs_for_project
from .status_web_templates import  status_web_templates
import time, logging, os



def print_bucket(job_name='server_status'):
    bucket = get_project_bucket(project=job_name)
    print_with_color('bucket: %s' % bucket, 'green')


def set_node_for_report(node, job_name='server_status'):
    set_project_node(project=job_name, node=node)
    bucket = get_project_bucket(project=job_name)
    print_with_color('node bucket: %s' % bucket, 'green')
    create_bucket_for_project(project=job_name)




def report_server_status_once(node, job_name='server_status_once'):
    set_node_for_report(node ,job_name=job_name)
    status_info = get_system_status(includes_processes=True, mini=True)
    create_record_for_project(project=job_name, message=status_info)
    print_bucket(job_name)


def report_server_status_always(node='', job_name='server_status', per_seconds=60, utc_offset=8):
    if not node:
        #print_with_color('need a node to report to, failed!')
        return # ignore
    # install logger
    os.environ['utc_offset'] = str(utc_offset)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger_handler = logging.FileHandler('/var/log/report_server_status.log')
    logger_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    logger_handler.setFormatter(formatter)

    logging.info('try to start %s' % job_name)
    for i in range(10):
        try:
            set_node_for_report(node ,job_name=job_name)
            bucket = get_project_bucket(job_name)
            logging.info('got bucket:%s' % bucket )
            break
        except:
            logging.info('failed to get a valid bucket')
            pass
        time.sleep(10)
    while True:
        try:
            status_info = get_system_status(includes_processes=True, mini=True)
            create_record_for_project(project=job_name, message=status_info)
            logging.info('reported')
        except:
            logging.info('report failed')
        time.sleep(per_seconds)




py_script_content = """#!/usr/bin/python
from xserver.server_status.report import report_server_status_always
if __name__ == '__main__':
    report_server_status_always(node='%s', utc_offset=%s)
"""


def get_report_server_status_cmd(node='', utc_offset=8):
    py_script_filepath = '/etc/init.d/report_server_status.py'
    script_content = py_script_content % (node, utc_offset)
    write_file(py_script_filepath, script_content)
    run_commands('chmod +x %s' % py_script_filepath)

    cmd = '/sbin/start-stop-daemon --start --background --exec %s'%py_script_filepath

    return cmd


def install_report_server_status(node='', utc_offset=8):
    #command = '/usr/local/bin/xserver_status report %s' % node
    #create_cronjob(command, on_reboot=True, write=True)
    cmd = get_report_server_status_cmd(node, utc_offset=utc_offset)
    create_cronjob(cmd, on_reboot=True, write=True)

    node = node.split('://', 1)[-1].strip('/')

    # 每隔 60 分钟检验一次, 避免突然退出
    try:
        utc_offset = float(utc_offset)
        utc_offset = round(utc_offset, 2)
    except:
        pass
    cmd = '/usr/local/bin/xserver_status start "%s" %s' % (node, utc_offset)
    create_cronjob(cmd, minutes=60, write=True)

    #create_cronjob(cmd, on_reboot=True, write=True)

    # 进行一次启动的逻辑, 如果已经启动了, 则不会起作用, 异步启动
    start_report_server_status(node=node, utc_offset=utc_offset)

    # 更新模板, 呈现 page
    project= 'server_status'

    while not get_project_bucket(project):
        print('wait the bucket project created then push web templates...')
        time.sleep(2)

    project_bucket = get_project_bucket(project)
    update_bucket_configs_for_project(project=project, configs=status_web_templates, config_type='pages')
    bucket_url = 'http://%s/bucket/%s/web' % (node, project_bucket)
    print('\n')
    print('visit %s to see the data' % bucket_url)




def start_report_server_status(node='', utc_offset=8):
    if not node:
        return
    matched_ps = get_matched_ps('report_server_status.py')
    if matched_ps:
        print_with_color('report_server_status is on running already', color='green')
    else:
        cmd = get_report_server_status_cmd(node, utc_offset=utc_offset)
        run_commands(cmd)


def stop_report_server_status():
    # report_server_s
    run_commands('start-stop-daemon --stop --name report_server_s')





