#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module flask_easylog.ui
---------------------------

ui for flask_easylog: change specificLevelLog by api

"""
from os.path import dirname, join
from flask_bluestatic import BlueStatic

class Ui(BlueStatic):
    def __init__(self, name='bluestatic', import_name=__name__, url_prefix="", *args, **kwargs):
        path = join(dirname(__file__), 'ui')
        BlueStatic.__init__(self, name, import_name, url_prefix, path, *args, **kwargs)