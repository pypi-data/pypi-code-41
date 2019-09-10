#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Environment module.

# File: mod_env.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Environment variables module
"""

import sys
import os
from os.path import abspath
from os.path import sep as SEP

MAX_WORKERS = 30
EOHMARK = """// END-OF-HEADER. DO NOT MODIFY OR DELETE THIS LINE"""
ADOCPROPS = {
    'source-highlighter'    :   'coderay',
    'stylesheet'            :   'kb4it.css',
    'stylesdir'             :   'resources/css',
    'imagesdir'             :   'resources/images',
    'scriptsdir'            :   'resources/js/jquery',
    'toc'                   :   'left',
    'toclevels'             :   '6',
    'icons'                 :   'font',
    'iconfont-remote!'      :   None,
    'iconfont-name'         :   'fontawesome-4.7.0',
    'experimental'          :   None,
    'linkcss'               :   None,
    'docinfo1'              :   'shared-header',
    'docinfo2'              :   'shared-footer',
    'docinfodir'            :   'resources/docinfo',
    #~ 'noheader'              :   None,
    #~ 'nofooter'              :   None,
}

ROOT = abspath(sys.modules[__name__].__file__ + "/../../")
USER_DIR = os.path.expanduser('~')

# App Info
APP = {}
APP['shortname'] = "KB4IT"
APP['name'] = "Knowledge Base For IT"
APP['license'] = "The code is licensed under the terms of the  GPL v3\n\
                  so you're free to grab, extend, improve and fork the \
                  code\nas you want"
APP['copyright'] = "Copyright \xa9 2019 Tomás Vírseda"
APP['desc'] = ""
APP['version'] = "0.6"
APP['authors'] = ["Tomás Vírseda <tomasvirseda@gmail.com>"]
APP['documenters'] = ["Tomás Vírseda <tomasvirseda@gmail.com>"]

# Local paths
LPATH = {}
LPATH['ROOT'] = USER_DIR + SEP + '.' + APP['shortname'].lower() + SEP
LPATH['ETC'] = LPATH['ROOT'] + 'etc' + SEP
LPATH['VAR'] = LPATH['ROOT'] + 'var' + SEP
LPATH['PLUGINS'] = LPATH['VAR'] + 'plugins' + SEP
LPATH['LOG'] = LPATH['VAR'] + 'log' + SEP
LPATH['TMP'] = LPATH['VAR'] + 'tmp' + SEP
LPATH['CACHE'] = LPATH['VAR'] + 'cache' + SEP
LPATH['DB'] = LPATH['VAR'] + 'db' + SEP
LPATH['WWW'] = LPATH['VAR'] + 'www' + SEP
LPATH['EXPORT'] = LPATH['VAR'] + 'export' + SEP
LPATH['OPT'] = LPATH['ROOT'] + 'opt' + SEP

# Global paths
GPATH = {}
GPATH['ROOT'] = ROOT + SEP
GPATH['DATA'] = GPATH['ROOT'] + SEP + 'kb4it' + SEP
GPATH['RESOURCES'] = GPATH['ROOT'] + 'resources' + SEP
GPATH['OFFLINE'] = GPATH['RESOURCES'] + 'offline' + SEP
GPATH['TEMPLATES'] = GPATH['OFFLINE'] + 'templates' + SEP
GPATH['ONLINE'] = GPATH['RESOURCES'] + 'online' + SEP
GPATH['SHARE'] = GPATH['DATA'] + 'share' + SEP
GPATH['DOC'] = GPATH['SHARE'] + 'docs' + SEP
GPATH['RES'] = GPATH['DATA'] + 'res' + SEP
GPATH['HELP'] = GPATH['DATA'] + 'help' + SEP
GPATH['HELP_HTML'] = GPATH['HELP'] + 'html' + SEP

# Configuration, SAP Notes Database and Log files
FILE = {}
FILE['CNF'] = LPATH['ETC'] + APP['shortname'].lower() + '.ini'
FILE['LOG'] = LPATH['LOG'] + APP['shortname'].lower() + '.log'
FILE['HELP_INDEX'] = GPATH['HELP_HTML'] + 'index.html'
