#coding: utf8
from __future__ import absolute_import, print_function
import os, re

def run_cmd(cmd, ignore_error=False):
    if ignore_error:
        try:
            f = os.popen(cmd)
            result = f.read()
            f.close()
        except:
            result = ''
    else:
        f = os.popen(cmd)
        result = f.read()
        f.close()
    return result


def run_cmds(cmds):
    results = []
    if not isinstance(cmds, (list, tuple)):
        cmds = cmds.split('\n')
    for cmd in cmds:
        cmd = cmd.strip()
        if cmd.startswith('#'):
            continue
        if not cmd:
            continue
        result = run_cmd(cmd)
        results.append(result)
    return results


def show_iptables_rules():
    rules = run_cmd('iptables -L')
    print(rules)



def remove_iptables_chain(chain_name):
    cmds = """
    iptables-save | grep -v "\-j %s" | iptables-restore
    iptables --flush %s
    iptables --delete-chain %s
    """ % (chain_name, chain_name, chain_name)
    run_cmds(cmds)
    show_iptables_rules()


def build_iptables_chain(vars_got):
    chain_name = ''
    port = 0
    ips = []
    if not isinstance(vars_got, (list, tuple)):
        vars_got = vars_got.split(' ')
    for v in vars_got:
        v = v.strip()
        if not v:
            continue
        if re.match('\d+\.\d+\.\d+\.\d+$', v): # append ip
            ip = v
            if ip not in ips:
                ips.append(ip)
        elif not port and re.match('\d+$', v): # got port
            port = v
        elif not chain_name and re.match('[a-z]\w+$', v, flags=re.I):
            chain_name = v
    if not chain_name or not port or not ips:
        print('must set chain_name & port & ips')
        return
    remove_iptables_chain(chain_name) # remove the chain first
    run_cmds("""
    iptables -N %(name)s
    iptables -I FORWARD -p tcp -m tcp --dport %(port)s -j %(name)s
    iptables -I INPUT -p tcp -m tcp --dport %(port)s -j %(name)s
    iptables -A %(name)s  -i lo -j ACCEPT
    """ % {'name': chain_name, 'port': port})
    run_cmd('iptables -A %s  -i docker0 -j ACCEPT'%chain_name, ignore_error=True)
    for ip in ips:
        run_cmd('iptables -A %s -s %s/32 -j ACCEPT' % (chain_name, ip))
    run_cmd('iptables  -A %s -j DROP' % chain_name)
    show_iptables_rules()




