# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.template.loaders.app_directories import app_template_dirs


def find_template(fname):
    """Find absolute path to template.
    """
    for dirname in tuple(settings.TEMPLATE_DIRS) + app_template_dirs:
        tmpl_path = os.path.join(dirname, fname)
        # print "TRYING:", tmpl_path
        if os.path.exists(tmpl_path):
            return tmpl_path

    raise IOError(fname + " not found.")
