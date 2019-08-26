# -*- coding: utf-8 -*-
"""Puzzlestream module statusbar module.

contains PSModuleStatusbar, a subclass of QGraphicsItemGroup
"""

from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class PSModuleStatusbar(QtWidgets.QGraphicsItemGroup):

    def __init__(self, initx: int, inity: int, width: int, height: int,
                 bgColor: str, frameColor="black", parent: QObject=None):

        super().__init__(parent=parent)

        self.__bgColor = bgColor
        self.__frameColor = frameColor
        self.__width = width
        self.__height = height

        self.__bgBrush = QBrush(QColor(self.__bgColor))
        self.__framePen = QPen(QColor(self.__frameColor))

        self.__rectItem = QtWidgets.QGraphicsRectItem(
            initx, inity, self.__width, self.__height
        )

        self.__rectItem.setPen(self.__framePen)
        self.__rectItem.setBrush(self.__bgBrush)

        self.__textItem = QtWidgets.QGraphicsTextItem()
        self.__textItem.setPlainText("")
        self.__textItem.setDefaultTextColor(Qt.white)
        self.__textItem.setPos(
            initx + (self.__width / 20), inity - (self.__height / 5))
        font = self.__textItem.font()
        font.setPixelSize(12)
        self.__textItem.setFont(font)

        self.addToGroup(self.__rectItem)
        self.addToGroup(self.__textItem)

    @property
    def bgColor(self) -> str:
        return self.__bgColor

    @bgColor.setter
    def bgColor(self, color: str):
        self.__bgColor = color
        self.__bgBrush = QBrush(QColor(self.__bgColor))
        self.__rectItem.setBrush(self.__bgBrush)

    @property
    def text(self) -> str:
        return self.__textItem.toPlainText()

    @text.setter
    def text(self, text: str):
        self.__textItem.setPlainText(text)

    @property
    def height(self) -> int:
        return self.__height
