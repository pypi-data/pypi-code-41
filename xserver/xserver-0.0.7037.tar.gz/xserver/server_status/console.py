#coding: utf8
from __future__ import absolute_import
from xserver import version
from xserver.utils.cli_color import print_with_color
from xserver.utils.console_utils import get_args_from_console, get_first_arg_from_console
from xserver.server_status.helper import print_server_status
from xserver.server_status.report import install_report_server_status, print_bucket, start_report_server_status, stop_report_server_status
import sys
try:
    from xserver.client.utils.fab import make_env, run_cmds
except:
    make_env, run_cmds = None, None


# xserver_status
# xserver_status install_report xx.xx.xx.xx:7788
# xserver_status report xx.xx.xx.xx:7788  # --> 实际是 crontab 中调用的, install_report 时候产生的
# xserver_status remote_install <ip> node,utc_offset
# xserver_status remote_update <ip> node,utc_offset

info_for_need_a_node = 'need a node, like xserver_status install domain_or_ip:7788'

def main():
    raw_args = sys.argv[2:]
    kwargs, args = get_args_from_console(raw_args)
    action = get_first_arg_from_console()
    if not action and not kwargs and not args:
        print_server_status()
    elif action in ['install', 'install_report', 'install_reporter']:
        if args:
            node = args[0]
            utc_offset = 8
            if len(args) >= 2:
                try: utc_offset = float(args[1])
                except: pass
            install_report_server_status(node, utc_offset)
        else:
            print_with_color(info_for_need_a_node)
    # todo 应该还有 uninstall 的逻辑？
    elif action in ['report', 'start', 'report_to']:
        if not args:
            print_with_color(info_for_need_a_node)
        else:
            node = args[0]
            utc_offset = 8
            if len(args) >= 2:
                try: utc_offset = float(args[1])
                except: pass
            start_report_server_status(node, utc_offset=utc_offset)
    elif action in ['stop', 'stop_report']:
        stop_report_server_status()
    elif action == 'remote_install' and make_env:
        ips = args[:-1]
        node_server_info = args[-1].replace(',', ' ')
        if not len(args)>=2:
            print_with_color("xserver_status remote_install <ips> node,utc_offset -> not matched")
            return
        for ip in ips:
            make_env(ip)
            run_cmds("""
                apt-get update
                apt-get install build-essential libssl-dev libffi-dev python-dev -y

                pip install setuptools -U
                pip install farbox_bucket -U
                pip install xserver==%s

                xserver_status install %s
                crontab -l
            """ % (version, node_server_info))
    elif action == 'remote_update' and make_env:
        ips = args[:-1]
        node_server_info = args[-1].replace(',', ' ')
        if not len(args)>=2:
            print_with_color("xserver_status remote_update <ips> node,utc_offset -> not matched")
            return
        for ip in ips:
            make_env(ip)
            run_cmds("""
                pip install xserver==%s
                xserver_status stop
                xserver_status install %s
                crontab -l
            """% (version,node_server_info))
    else:
        print_with_color('fail to match command for xserver_status', color='red')




if __name__ == '__main__':
    main()