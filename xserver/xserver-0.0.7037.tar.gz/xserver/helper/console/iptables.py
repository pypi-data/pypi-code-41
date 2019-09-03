#coding: utf8
from __future__ import absolute_import
from xserver.utils.console_utils import get_args_from_console, get_first_arg_from_console
import sys

from xserver.utils.iptables import build_iptables_chain, remove_iptables_chain


def main():
    raw_args = sys.argv[2:]
    kwargs, args = get_args_from_console(raw_args)
    action = get_first_arg_from_console()
    if action == 'build':
        build_iptables_chain(args)
    elif action == 'remove':
        if not args:
            print('please set a chain_name to remove')
        else:
            for chain_name in args:
                remove_iptables_chain(chain_name)
    else:
        print('failed, xserver_iptables build/remove ......')


if __name__ == '__main__':
    main()