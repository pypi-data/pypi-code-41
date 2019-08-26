# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from puzzlestream.backend.stream import PSStream
from puzzlestream.apps.base import PSApp, PSAppGUIWidget

app = "PS1DPlotApp"
name = "1D plot"
# icon = "icon.png"


class PS1DPlotApp(PSApp):

    def __init__(self, data: dict, **pars):
        super().__init__(data, **pars)
        self._guiWidgetClass = PS1DPlotAppGUI

    @property
    def code(self) -> str:
        return super().code

    def setParameters(self, **pars):
        super().setParameters(**pars)


class PS1DPlotAppGUI(PSAppGUIWidget):

    def __init__(self, app: PSApp, parent=None):
        super().__init__(app, parent=parent)
        self.__app = app
        self.__layout = QGridLayout()
        self.setLayout(self.__layout)
        self.__layout.addWidget(QLabel("Plot"), 0, 0)

    def reload(self):
        pass

    def retranslateUi(self):
        pass
