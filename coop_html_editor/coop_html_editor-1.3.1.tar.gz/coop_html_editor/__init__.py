# -*- coding: utf-8 -*-
"""coop_html_editor : use Inline Html Editor in Django project"""

VERSION = (1, 3, 1)


def get_version():
    """return version"""
    version = '%s.%s.%s' % (VERSION[0], VERSION[1], VERSION[2])
    return version


__version__ = get_version()

default_app_config = 'coop_html_editor.apps.CoopHtmlEditorAppConfig'
