# -*- coding:utf8 -*-
from service.output.pexpectInput import PexpectClient
from constants.PasswordErrorException import PasswordErrorException
import os
from optparse import OptionParser
from constants.ParamsException import ParamsException
import sys
from pexpect.exceptions import TIMEOUT
from api.api import Api
from api.inputClient import InputClient
from api.outputClient import OutputClient


def main():
    inputClient = InputClient()
    api = Api()
    usage = "usage: %prog [options] [arg]"
    parser = OptionParser(usage)
    parser.add_option('-l', '--list', action='store_true', dest="iflist", help=u"列出所有的ssh连接")
    parser.add_option('-a', '--add', action='store_true', dest="ifadd", help=u"添加ssh连接")
    parser.add_option('-i', '--host', action="store", dest="host", help=u"连接的host")
    parser.add_option('-d', action='store',dest='del_host', help=u"删除ssh连接")
    parser.add_option('-D', '--delete-by-index', action='store_true', dest='del_by_index', help=u"通过index删除ssh连接")
    parser.add_option('-u','--update', action="store_true",dest="ifupdate")
    # parser.add_option('-')

    (option, args) = parser.parse_args()
    opt_dict = eval(str(option))
    opt_values = opt_dict.values()
    param_len = len(opt_values) - opt_values.count(None)
    output = OutputClient()
    output.set_header(['index','Host','UserName'], [7,17,15])
    if param_len > 1:
        raise ParamsException('参数错误')
    elif param_len == 0:
        if len(args) > 0:
            host = args[0]
            ssh_conn = api.get_ssh_connect(host)
            if ssh_conn is not None:
                api.login(ssh_conn.get('host'),ssh_conn.get('name'), ssh_conn.get('passwd'))
            else:
                ssh_conns = api.login_fuzzy(host)
                con_len = len(ssh_conns)
                if con_len == 0:
                    sys.stdout.write("没有匹配的Host!\n")
                    return
                elif con_len == 1:
                    api.login(ssh_conns[0].get('host'),ssh_conns[0].get('name'), ssh_conns[0].get('passwd'))
                    return
                else:
                    output.set_values(ssh_conns)
                    sys.stdout.write(output.show())
                    sys.stdout.write('\n')
                    ssh_conn = output.select()
                    api.login(ssh_conn.get('host'), ssh_conn.get('name'), ssh_conn.get('passwd'))
                    return
            return
        else:
            ssh_conns = api.list_ssh_connects()
            output.set_values(ssh_conns)
            # print output.show()
            sys.stdout.write(output.show())
            sys.stdout.write('\n')
            if len(ssh_conns) > 0:
                ssh_conn = output.select()
                api.login(ssh_conn.get('host'),ssh_conn.get('name'), ssh_conn.get('passwd'))
            return
    else:
        iflist = option.iflist
        ifadd = option.ifadd
        host = option.host
        ifupdate = option.ifupdate
        del_host = option.del_host
        del_by_index = option.del_by_index
        try:
            if iflist:
                ssh_conns = api.list_ssh_connects()
                # print ssh_conns
                output.set_values(ssh_conns)
                sys.stdout.write(output.show())
                sys.stdout.write('\n')
                return
            if ifadd:
                host = inputClient.input_host()
                username = inputClient.input_username()
                password = inputClient.input_password()
                api.add_ssh_connect(host, username, password)
                # print host, username, password
                return
            if host:
                ssh_conn = api.get_ssh_connect(host)
                if ssh_conn is None:
                    raise Exception("错误: 主机 %s 不存在!" % host)
                else:
                    api.login(ssh_conn.get('host'), ssh_conn.get('name'), ssh_conn.get('passwd'))
            if ifupdate:
                ssh_conns = api.list_ssh_connects()
                # print ssh_conns
                output.set_values(ssh_conns)
                sys.stdout.write(output.show())
                sys.stdout.write('\n')
                if len(ssh_conns) > 0:
                    ssh_conn = output.select_to_update()
                    username = inputClient.input_username()
                    password = inputClient.input_password()
                    api.update_ssh_connect(ssh_conn.get('host'), username, password)
                    sys.stdout.write('更新成功!\n')
            if del_host:
                ssh_conn = api.get_ssh_connect(del_host)
                if ssh_conn is None:
                    raise Exception("错误: 主机 %s 不存在!" % host)
                api.del_ssh_connect(del_host)
                sys.stdout.write('删除成功!\n')
            if del_by_index:
                ssh_conns = api.list_ssh_connects()
                # print ssh_conns
                output.set_values(ssh_conns)
                sys.stdout.write(output.show())
                sys.stdout.write('\n')
                if len(ssh_conns) > 0:
                    ssh_conn = output.select_to_del()
                    api.del_ssh_connect(ssh_conn.get('host'))
                    sys.stdout.write('删除成功!\n')
                return
        except ParamsException as e:
            sys.stdout.write(e.msg)
            sys.stdout.write('\n')
        except TIMEOUT as e:
            sys.stdout.write("连接超时!\n")
        except Exception as e:
            sys.stdout.write(e.message)
            sys.stdout.write('\n')


def intur_hander(signal, frame):
    sys.exit(0)


if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, intur_hander)
    main()
