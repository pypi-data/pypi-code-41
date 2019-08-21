#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" example wa_hack_cli client """
from wa_hack_cli import simple_send, CommandLineInterface

if __name__ == "__main__":

    # SRV = '192.168.123.38'
    SRV = '127.0.0.1'
    PORT = 9009
    RECIPIENT = '+491717626871'
    TEXT = 'test'

    CLI = CommandLineInterface()
    CLI.start()
