# -*- coding: utf-8 -*-

# Copyright (c) 2014 - 2019 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing some common utility functions for the Git package.
"""

from __future__ import unicode_literals

import os
import sys

from PyQt5.QtCore import QProcessEnvironment, QByteArray

import Utilities


def getConfigPath():
    """
    Public function to get the filename of the config file.
    
    @return filename of the config file (string)
    """
    if Utilities.isWindowsPlatform():
        userprofile = os.environ["USERPROFILE"]
        return os.path.join(userprofile, ".gitconfig")
    else:
        homedir = Utilities.getHomeDir()
        return os.path.join(homedir, ".gitconfig")


def prepareProcess(proc, language=""):
    """
    Public function to prepare the given process.
    
    @param proc reference to the process to be prepared (QProcess)
    @param language language to be set (string)
    """
    env = QProcessEnvironment.systemEnvironment()
    
    # set the language for the process
    if language:
        env.insert("LANGUAGE", language)
    
    proc.setProcessEnvironment(env)


try:
    from Globals import strToQByteArray
except ImportError:
    def strToQByteArray(txt):
        """
        Module function to convert a Python string into a QByteArray.
        
        @param txt Python string to be converted
        @type str, bytes, bytearray, unicode
        """
        if sys.version_info[0] == 2:
            if isinstance(txt, unicode):    # __IGNORE_WARNING__
                txt = txt.encode("utf-8")
        else:
            if isinstance(txt, str):
                txt = txt.encode("utf-8")
        
        return QByteArray(txt)
