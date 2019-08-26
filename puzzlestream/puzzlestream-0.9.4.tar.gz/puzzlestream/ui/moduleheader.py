# -*- coding: utf-8 -*-
"""Puzzlestream module header module.

contains PSModuleHeader, a subclass of QGraphicsRectItem
"""

from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class PSModuleHeader(QtWidgets.QGraphicsRectItem):

    def __init__(self, initx: int, inity: int, width: int, height: int,
                 bgColor: str, frameColor="black", parent: QObject = None):

        self.__bgColor = bgColor
        self.__frameColor = frameColor
        self.__width = width
        self.__height = height

        self.__bgBrush = QBrush(QColor(self.__bgColor))
        self.__framePen = QPen(QColor(self.__frameColor))

        super().__init__(initx, inity,
                         self.__width, self.__height, parent=parent)

        self.setPen(self.__framePen)
        self.setBrush(self.__bgBrush)

    @property
    def bgColor(self) -> str:
        return self.__bgColor

    @bgColor.setter
    def bgColor(self, color: str):
        self.__bgColor = color
        self.__bgBrush = QBrush(QColor(self.__bgColor))
        self.setBrush(self.__bgBrush)

    @property
    def height(self) -> int:
        return self.__height
