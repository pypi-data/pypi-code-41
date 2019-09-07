#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2019 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Eric6 Web Browser.

This is the main Python script that performs the necessary initialization
of the web browser and starts the Qt event loop. This is a standalone version
of the integrated helpviewer.
"""

from __future__ import unicode_literals

import sys
import os

sys.path.insert(1, os.path.dirname(__file__))

import Toolbox.PyQt4ImportHook  # __IGNORE_WARNING__

try:  # Only for Py2
    import Globals.compatibility_fixes     # __IGNORE_WARNING__
except (ImportError):
    pass

try:
    try:
        from PyQt5 import sip
    except ImportError:
        import sip
    sip.setdestroyonexit(False)
except AttributeError:
    pass

try:
    from PyQt5 import QtWebKit      # __IGNORE_WARNING__
except ImportError:
    if "--quiet" not in sys.argv:
        from PyQt5.QtCore import qVersion, QTimer
        from PyQt5.QtWidgets import QApplication
        from E5Gui import E5MessageBox
        app = QApplication([])
        QTimer.singleShot(0, lambda: E5MessageBox.critical(
            None,
            "eric6 Web Browser (QtWebKit based)",
            "QtWebKit is needed to run this variant of the eric6 Web Browser."
            " However, it seems to be missing. You are using Qt {0}, which"
            " doesn't include this anymore.".format(qVersion())))
        app.exec_()
    sys.exit(100)

for arg in sys.argv[:]:
    if arg.startswith("--config="):
        import Globals
        configDir = arg.replace("--config=", "")
        Globals.setConfigDir(configDir)
        sys.argv.remove(arg)
    elif arg.startswith("--settings="):
        from PyQt5.QtCore import QSettings
        settingsDir = os.path.expanduser(arg.replace("--settings=", ""))
        if not os.path.isdir(settingsDir):
            os.makedirs(settingsDir)
        QSettings.setPath(QSettings.IniFormat, QSettings.UserScope,
                          settingsDir)
        sys.argv.remove(arg)

# make ThirdParty package available as a packages repository
sys.path.insert(2, os.path.join(os.path.dirname(__file__),
                                "ThirdParty", "Pygments"))
sys.path.insert(2, os.path.join(os.path.dirname(__file__),
                                "ThirdParty", "EditorConfig"))

import Globals
from Globals import AppInfo

from E5Gui.E5Application import E5Application

from Toolbox import Startup

from Helpviewer.HelpSingleApplication import HelpSingleApplicationClient

app = None


def createMainWidget(argv):
    """
    Function to create the main widget.
    
    @param argv list of command line parameters
    @type list of str
    @return reference to the main widget
    @rtype QWidget
    """
    from Helpviewer.HelpWindow import HelpWindow
    
    searchWord = None
    qthelp = False
    single = False
    name = ""
    
    for arg in reversed(argv):
        if arg.startswith("--search="):
            searchWord = argv[1].split("=", 1)[1]
            argv.remove(arg)
        elif arg.startswith("--name="):
            name = arg.replace("--name=", "")
            argv.remove(arg)
        elif arg.startswith("--newtab="):
            # only used for single application client
            argv.remove(arg)
        elif arg == "--qthelp":
            qthelp = True
            argv.remove(arg)
        elif arg == "--quiet":
            # only needed until we reach this point
            argv.remove(arg)
        elif arg == "--single":
            single = True
            argv.remove(arg)
        elif arg.startswith("--"):
            argv.remove(arg)
    
    try:
        home = argv[1]
    except IndexError:
        home = ""
    
    helpWindow = HelpWindow(home, '.', None, 'help viewer',
                            searchWord=searchWord, qthelp=qthelp,
                            single=single, saname=name)
    return helpWindow


def main():
    """
    Main entry point into the application.
    """
    global app
    
    options = [
        ("--config=configDir",
         "use the given directory as the one containing the config files"),
        ("--qthelp", "start the browser with support for QtHelp"),
        ("--quiet", "don't show any startup error messages"),
        ("--search=word", "search for the given word"),
        ("--settings=settingsDir",
         "use the given directory to store the settings files"),
        ("--single", "start the browser as a single application"),
    ]
    appinfo = AppInfo.makeAppInfo(sys.argv,
                                  "eric6 Web Browser",
                                  "file",
                                  "web browser",
                                  options)
    
    # set the library paths for plugins
    Startup.setLibraryPaths()
    
    app = E5Application(sys.argv)
    client = HelpSingleApplicationClient()
    res = client.connect()
    if res > 0:
        if len(sys.argv) > 1:
            client.processArgs(sys.argv[1:])
        sys.exit(0)
    elif res < 0:
        print("eric6_webbrowser: {0}".format(client.errstr()))
        # __IGNORE_WARNING_M801__
        sys.exit(res)
    
    res = Startup.simpleAppStartup(sys.argv,
                                   appinfo,
                                   createMainWidget,
                                   installErrorHandler=True,
                                   app=app)
    sys.exit(res)

if __name__ == '__main__':
    main()
