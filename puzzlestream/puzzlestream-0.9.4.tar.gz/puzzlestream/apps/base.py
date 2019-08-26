# -*- coding: utf-8 -*-

from typing import Callable

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from puzzlestream.backend.stream import PSStream
from puzzlestream.backend.streamsection import PSStreamSection

translate = QCoreApplication.translate


class PSApp:

    def __init__(self, data: dict, **pars):
        self.data = data
        self._guiWidgetClass = PSAppGUIWidget
        self.setParameters(**pars)

    @property
    def code(self) -> str:
        text = "from puzzlestream.apps import " + self.__class__.__name__
        text += "\next = " + self.__class__.__name__ + "(\n    stream"
        for key in self.__pars:
            text += ",\n    %s=%s" % (key, str(self.__pars[key]))
        text += "\n)"
        return text

    @property
    def data(self) -> dict:
        return self.__data

    @data.setter
    def data(self, data: dict):
        self.__data = data

    def showGUI(self, ID: int, modules: dict, stream: PSStream, parent=None):
        PSAppGUI(self, ID, modules, stream, self._guiWidgetClass,
                 parent=parent).show()

    def copyCode(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.code)

    def setParameters(self, **pars):
        self.__pars = pars


class PSAppGUI(QMainWindow):

    def __init__(self, app: PSApp, ID: int, modules: dict, stream: PSStream,
                 widgetClass, parent=None, *args):
        super().__init__(*args, parent=parent)
        self.__widget = QWidget()
        self.__id = ID
        self.__app = app
        self.__stream = stream
        self.__modules = modules
        self.__moduleChanger = QComboBox()
        self.__moduleIDs = []
        self.fillModuleChanger()
        self.__moduleChanger.currentIndexChanged.connect(self.__moduleChanged)
        self.__appWidget = widgetClass(app)
        self.__btnCopyCode = QPushButton("Copy code")
        self.__btnCopyCode.clicked.connect(self.__copyCode)
        self.__layout = QGridLayout()
        self.__widget.setLayout(self.__layout)
        self.__layout.addWidget(self.__moduleChanger, 0, 0, 1, 3)
        self.__layout.addWidget(self.__appWidget, 1, 0, 1, 3)
        self.__layout.addWidget(self.__btnCopyCode, 2, 0, 1, 1)
        self.setCentralWidget(self.__widget)

        self.retranslateUi()

    def fillModuleChanger(self):
        self.__moduleChanger.clear()
        self.__moduleIDs.clear()
        for m in sorted(self.__modules.values()):
            self.__moduleChanger.addItem(m.name)
            self.__moduleIDs.append(m.id)
        current = self.__moduleIDs.index(self.__id)
        self.__moduleChanger.setCurrentIndex(current)

    def __moduleChanged(self, index: int):
        data = PSStreamSection(self.__moduleIDs[index], self.__stream).data
        self.__app.data = data
        self.__id = self.__moduleIDs[index]
        self.__appWidget.reload()

    def __copyCode(self):
        self.__app.copyCode()
        self.__btnCopyCode.setText(
            translate("AppGUI", "Code copied to clipboard"))
        t = QTimer()
        t.singleShot(1000, self.__resetCopyBtnText)

    def __resetCopyBtnText(self):
        self.__btnCopyCode.setText(translate("AppGUI", "Copy code"))

    def retranslateUi(self):
        self.__resetCopyBtnText()
        self.__appWidget.retranslateUi()


class PSAppGUIWidget(QWidget):

    def __init__(self, app: PSApp, parent=None):
        super().__init__(parent=parent)
        self.__app = app

    def reload(self):
        raise NotImplementedError()

    def retranslateUi(self):
        raise NotImplementedError()
