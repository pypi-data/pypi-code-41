# -*- coding: utf-8 -*-

# Copyright (c) 2014 - 2019 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module defining configuration variables for the Git package.
"""

from __future__ import unicode_literals

# Available protocols for the repository URL
ConfigGitSchemes = [
    'file',
    'ftp',
    'ftps',
    'git',
    'http',
    'https',
    'rsync',
    'ssh',
    'ssh+scp',
]
