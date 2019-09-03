#coding: utf8
from __future__ import absolute_import
from xserver.client.utils.fab import run, make_env, sudo


# 服务器初始化的时候的基本环境构建
def create_mini_env(ip=None):
    if ip:
        make_env(ip)

    run('apt-get update')
    run('apt-get install -y ntp ntpdate lsof ethstatus iotop gcc')
    run('apt-get install -y wget python-dev python-pip nano')



# 指定系统的 DNS 解析服务
def configs_dns_servers(dns_servers=None):
    if dns_servers and isinstance(dns_servers, (list, tuple)):
        pass
    else:
        dns_servers = ['8.8.8.8', '8.8.4.4']
    # 处理dns解析的设定
    nameserver_list = []
    for dns_server in dns_servers:
        nameserver_list.append('nameserver %s'%dns_server)
    dns_config = '\n'.join(nameserver_list)
    command1 = 'echo -e "%s" > /etc/resolv.conf' % dns_config
    command2 = 'echo -e "%s" > /etc/resolvconf/resolv.conf.d/tail' % dns_config
    run(command1)
    try:
        run(command2)
        sudo('resolvconf -u')
    except:
        pass

# docker 环境的基本构建



