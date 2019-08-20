# -*- coding: utf-8 -*-
'''
    wumappy.gui.common.warningdlgbox
    --------------------------------

    Warning dialog box management.

    :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''

from __future__ import absolute_import
import os
import numpy as np

#from Qt import QtCore, QtWidgets # Qt.py is a shim around all Qt bindings
#from Qt import __binding__
from Qt.QtCore import *
from Qt.QtGui import *
from Qt.QtWidgets import *

#from geophpy.dataset import *

#---------------------------------------------------------------------------#
# Display Warning Dialog Box Object                                          #
#---------------------------------------------------------------------------#
class WarningDlgBox(QDialog):
    
    def __init__(self, title, parent, message):
        '''
        Parameters :
        :title: title of dialog box
        :parent: parent windows object
        :message: message ti display in the dialog box
        '''
        super(WarningDlgBox, self).__init__()

        self.asciiset = parent.asciiset
        self.icon = parent.icon

        self.setWindowTitle(title)                  # sets the windows title
        self.setWindowIcon(self.icon)               # sets the window icon
        self.setFont(self.asciiset.font)

        self.layout = QGridLayout()           # builds the main layout
                                                    # the main layout will be composed by layouts as columns

        logo = os.path.abspath(os.path.join(parent.resources_path, 'warning.PNG'))
        icon = QIcon(logo)
        self.layout.addWidget(icon, 0, 0)


        self.setLayout(self.layout)
