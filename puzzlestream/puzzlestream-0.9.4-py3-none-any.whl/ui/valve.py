# -*- coding: utf-8 -*-
"""Puzzlestream valve module.

contains PSValve, a subclass of PSDockItem
"""

from typing import Callable

from puzzlestream.backend.status import PSStatus
from puzzlestream.backend.stream import PSStream
from puzzlestream.ui import colors
from puzzlestream.ui.puzzledockitem import PSPuzzleDockItem
from puzzlestream.ui.puzzleitem import PSPuzzleItem
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QBrush, QColor, QPen


class PSValve(PSPuzzleDockItem):

    def __init__(self, valveID: int, streamSectionSupplier: Callable,
                 x: float, y: float):
        """
        =======================================================================
            Define GUI appearence: geometry and position
        """
        self._width = 150
        self._height = 150
        self.__centerDiameter = 40
        self.__pipeLength = 75
        self.__pipewidth = 40
        self.__centralCircle = None
        self.__connectionPipes = None

        super().__init__(valveID, streamSectionSupplier)

        self._radius = self.__pipeLength + self._dockHeight

        """
        =======================================================================
            Initialisation of backendstructure
        """

        self.__inputPipes = []
        self.numberOfOutputs = 0
        self.__allInputsRun = False
        self.propagateIncompleteInputs = True

        """
        =======================================================================
            Initialise GUI components:
        """
        self.__bgBrush = QBrush(QColor(colors.get("standard-blue")))
        self.__createConnectionPipes()

        self.__centralCircle = QtWidgets.QGraphicsEllipseItem(
            self.__pipeLength - self.__centerDiameter / 2,
            self.__pipeLength - self.__centerDiameter / 2,
            self.__centerDiameter,
            self.__centerDiameter,
            parent=self
        )
        self.__centralCircle.setBrush(self.__bgBrush)

        self.setCenterPos(QtCore.QPointF(x, y))

    def __createConnectionPipes(self):
        self.__connectionPipes = []

        for position in self._positionIndex:
            connectionPipe = QtWidgets.QGraphicsRectItem(
                0, 0, 40, 75, parent=self
            )
            connectionPipe.setBrush(self.__bgBrush)
            connectionPipe.hide()
            self.__connectionPipes.append(connectionPipe)

        topPipe = self.__connectionPipes[self._positionIndex["top"]]
        topPipe.setPos(self.centerPos().x() - self.__pipewidth / 2,
                       self.centerPos().y() - self.__pipeLength)

        leftPipe = self.__connectionPipes[self._positionIndex["left"]]
        leftPipe.setRotation(90)
        leftPipe.setPos(self.centerPos().x(),
                        self.centerPos().y() - self.__pipewidth / 2)

        bottomPipe = self.__connectionPipes[self._positionIndex["bottom"]]
        bottomPipe.setPos(self.centerPos().x() - self.__pipewidth / 2,
                          self.centerPos().y())

        rightPipe = self.__connectionPipes[self._positionIndex["right"]]
        rightPipe.setRotation(90)
        rightPipe.setPos(self.centerPos().x() + self.__pipeLength,
                         self.centerPos().y() - self.__pipewidth / 2)

    def __updatePattern(self):
        if self.autopass:
            self.__bgBrush.setColor(QColor(colors.get("standard-blue")))
            self.__bgBrush.setStyle(QtCore.Qt.SolidPattern)
        else:
            self.__bgBrush.setColor(QColor(colors.get("light-blue")))
            self.__bgBrush.setStyle(QtCore.Qt.BDiagPattern)

        for p in self.__connectionPipes:
            p.setBrush(self.__bgBrush)

    def __str__(self) -> str:
        return "Valve " + str(self.id)

    def __repr__(self) -> str:
        return "Valve " + str(self.id)

    @property
    def __shift(self) -> QtCore.QPointF:
        return QtCore.QPointF(self.__pipeLength, self.__pipeLength)

    def centerPos(self) -> QtCore.QPointF:
        return self.pos() + self.__shift

    def setCenterPos(self, point: QtCore.QPointF):
        self.setPos(point - self.__shift)

    @property
    def saveProperties(self) -> dict:
        props = {"numberOfOutputs": self.numberOfOutputs,
                 "inPipeIDs": [p.id for p in self.__inputPipes],
                 "propagateIncompleteInputs": self.propagateIncompleteInputs}
        props.update(super().saveProperties)
        return props

    def restoreProperties(self, props: dict, stream: PSStream):
        super().restoreProperties(props, stream)
        self.__updatePattern()
        if "propagateIncompleteInputs" in props:
            self.propagateIncompleteInputs = props["propagateIncompleteInputs"]

    def inputUpdate(self, pipe):
        self.stopHere = pipe.stopHere

        if pipe.status == "finished":
            self.streamSection.addSection(pipe.streamSection)

        statusses = [p.status for p in self.__inputPipes]
        if all([s is PSStatus.WAITING for s in statusses]):
            self.__allInputsRun = True

        if PSStatus.WAITING in statusses or PSStatus.RUNNING in statusses:
            self.status = PSStatus.WAITING
        elif "paused" in statusses:
            self.status = PSStatus.PAUSED
        elif "incomplete" in statusses:
            self.status = PSStatus.INCOMPLETE
        else:
            oldAutopass = self.autopass

            if not self.__allInputsRun and not self.propagateIncompleteInputs:
                self.status = PSStatus.INCOMPLETE
            else:
                self.status = PSStatus.FINISHED

            self.__allInputsRun = False

    def toggleOpenClosed(self):
        if self.autopass:
            self.autopass = False
        else:
            self.autopass = True
        self.__updatePattern()

    def togglePropagateIncompleteInputs(self):
        if self.propagateIncompleteInputs:
            self.propagateIncompleteInputs = False
        else:
            self.propagateIncompleteInputs = True

    @property
    def inputItems(self) -> list:
        return self.__inputPipes

    @property
    def inputPipes(self) -> list:
        return self.__inputPipes

    @property
    def numberOfInputs(self) -> int:
        return len(self.__inputPipes)

    @property
    def hasInput(self) -> bool:
        return self.numberOfInputs > 0

    @property
    def hasOutput(self) -> bool:
        return self.numberOfOutputs > 0

    """
    ===========================================================================
        Connection routines
    """

    def __addInputPipe(self, pipe):
        pipe.statusChanged.connect(self.inputUpdate)
        pipe.hasOutput = True
        self.__inputPipes.append(pipe)

    def __disconnectInputPipe(self, pipe):
        pipe.statusChanged.disconnect(self.inputUpdate)
        pipe.hasOutput = False
        i = self.__inputPipes.index(pipe)
        del self.__inputPipes[i]

    def establishConnection(self, otherItem: PSPuzzleItem,
                            silent: bool = False):
        self.__addInputPipe(otherItem)
        return super().establishConnection(otherItem, silent)

    def removeConnection(self, otherItem: PSPuzzleItem):
        self.__disconnectInputPipe(otherItem)
        super().removeConnection(otherItem)

    def _hidePosition(self, position: str):
        super()._hidePosition(position)
        if self.__connectionPipes is not None:
            if self.__centralCircle is not None:
                self.__centralCircle.hide()

            self.__connectionPipes[self._positionIndex[position]].hide()

            if self.__centralCircle is not None:
                self.__centralCircle.show()

    def _showPosition(self, position: str):
        super()._showPosition(position)
        if self.__connectionPipes is not None:
            if self.__centralCircle is not None:
                self.__centralCircle.hide()

            self.__connectionPipes[self._positionIndex[position]].show()

            if self.__centralCircle is not None:
                self.__centralCircle.show()
