#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2019 Taylor C. Richberger
# This code is released under the license described in the LICENSE file

import argparse

class License(argparse.Action):
    '''Simple license printer.  Prints the license and exits.'''
    def __init__(self, option_strings, dest, license, help=None, default=None):
        super().__init__(
            option_strings=option_strings,
            help=help,
            nargs=0,
            dest=dest,
        )
        self.license = license

    def __call__(self, parser, namespace, values, option_string):
        print(self.license)
        parser.exit()
