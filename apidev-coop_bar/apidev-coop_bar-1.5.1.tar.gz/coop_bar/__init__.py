# -*- coding: utf-8 -*-

from __future__ import unicode_literals

VERSION = (1, 5, 1)


def get_version():
    """version"""
    return '%s.%s.%s' % (VERSION[0], VERSION[1], VERSION[2])

__version__ = get_version()

default_app_config = 'coop_bar.apps.CoopBarAppConfig'
