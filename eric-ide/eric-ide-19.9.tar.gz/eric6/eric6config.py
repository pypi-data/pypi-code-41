# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2019 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module containing the default configuration of the eric6 installation.
"""

from __future__ import unicode_literals

import os

__ericDir = os.path.dirname(__file__)

_pkg_config = {
    'ericDir': __ericDir,
    'ericPixDir': os.path.join(__ericDir, 'pixmaps'),
    'ericIconDir': os.path.join(__ericDir, 'icons'),
    'ericDTDDir': os.path.join(__ericDir, 'DTDs'),
    'ericCSSDir': os.path.join(__ericDir, 'CSSs'),
    'ericStylesDir': os.path.join(__ericDir, "Styles"),
    'ericDocDir': os.path.join(__ericDir, 'Documentation'),
    'ericExamplesDir': os.path.join(__ericDir, 'Examples'),
    'ericTranslationsDir': os.path.join(__ericDir, 'i18n'),
    'ericTemplatesDir': os.path.join(__ericDir, 'DesignerTemplates'),
    'ericCodeTemplatesDir': os.path.join(__ericDir, 'CodeTemplates'),
    'ericOthersDir': __ericDir,
    'bindir': __ericDir,
    'mdir': __ericDir,
}


def getConfig(name):
    """
    Module function to get a configuration value.

    @param name name of the configuration value
    @type str
    @return requested config value
    @exception AttributeError raised to indicate an invalid config entry
    """
    try:
        return _pkg_config[name]
    except KeyError:
        pass

    raise AttributeError(
        '"{0}" is not a valid configuration value'.format(name))
