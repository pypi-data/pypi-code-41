#-------------------------------------------------------------------------------
# Name:        PIDTuneMethodsAboutWindow
# Purpose:
#
# Author:      ElBar
#
# Created:     10/06/2014
# Copyright:   (c) ElBar 2014
# Licence:     LGPL
#-------------------------------------------------------------------------------
#!/usr/bin/env python

from PyQt5 import QtGui, QtCore, QtWidgets
from Ui_pid_tune_methods_about_window import Ui_About

_VERSION = "0.3.4"
_URL = "<a href = ""http://sourceforge.net/projects/pypidtunemethods"">Sourceforge Project Home Page</a>"

#-------------------------------------------------------------------------------
class PIDTuneMethodsAboutWindow(QtWidgets.QDialog):
    """ Class wrapper for about window ui """

    def __init__(self):
        super(PIDTuneMethodsAboutWindow,self).__init__()
        self.setupUI()

    def setupUI(self):
        #create window from ui
        self.ui=Ui_About()
        self.ui.setupUi(self)
        self.ui.lblVersion.setText("pyPIDTuneMethods v{0}".format(_VERSION))
        self.ui.lblURL.setText(_URL)
#-------------------------------------------------------------------------------