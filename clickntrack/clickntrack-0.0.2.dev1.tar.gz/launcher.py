#!/usr/bin/python
# -*- coding: utf-8 -*-

import getopt
import logging
import logging.config
import sys

from clickntrack import webservices
from monkey.ioc.core import Registry

_CMD_LINE_HELP = 'launcher.py -h <host> -p <port> -f <path to config file>'


def _read_opts(argv):
    host = 'localhost'
    port = '8080'
    config_file = 'conf/main.json'
    try:
        opts, args = getopt.getopt(argv[1:], "?h:p:f:")
    except getopt.GetoptError as err:
        print(err)
        print(_CMD_LINE_HELP)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-?':
            print(_CMD_LINE_HELP)
            sys.exit()
        elif opt in '-h':
            host = arg
        elif opt in '-p':
            port = arg
        elif opt in '-f':
            config_file = arg
    return host, port, config_file


def launch(argv):
    host, port, config_file = _read_opts(argv)

    logging.config.fileConfig('logging.conf')

    registry = Registry()
    registry.load(config_file)

    try:
        logging_conf_file = registry.get('logging_conf', 'logging_conf')
        logging.config.fileConfig(logging_conf_file, disable_existing_loggers=True)
    except FileNotFoundError as e:
        print(e)

    webservices.start(registry, host, port)


if __name__ == '__main__':  # pragma: no coverage
    launch(sys.argv)

