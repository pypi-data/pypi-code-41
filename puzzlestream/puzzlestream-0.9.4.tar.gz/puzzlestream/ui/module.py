# -*- coding: utf-8 -*-
"""Puzzlestream module module.

contains PSModule, a subclass of PSPuzzleDockItem
"""

import os
from datetime import datetime
from time import time

from puzzlestream.backend import notificationsystem
from puzzlestream.backend.signal import PSSignal
from puzzlestream.backend.status import PSStatus
from puzzlestream.backend.stream import PSStream
from puzzlestream.backend.worker import PSWorker
from puzzlestream.ui import colors
from puzzlestream.ui.moduleheader import PSModuleHeader
from puzzlestream.ui.modulestatusbar import PSModuleStatusbar
from puzzlestream.ui.modulewidget import PSModuleWidget
from puzzlestream.ui.puzzledockitem import PSPuzzleDockItem
from puzzlestream.ui.puzzleitem import PSPuzzleItem
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QBrush, QColor, QPen

translate = QtCore.QCoreApplication.translate


class PSModule(PSPuzzleDockItem):

    def __init__(self, moduleID, x, y, path, name,
                 streamSectionSupplier, workerRegistrationFunction,
                 startTimerFunction, libs):
        """
        =======================================================================
            Object Initialisation and GUI Appearence
        """
        # Full PSModule geometry (header and statusbar inclusive)
        self._width = 150
        self._height = 150

        # PuzzleDockItem -> PuzzleItem -> QGraphicsItem
        super().__init__(moduleID, streamSectionSupplier)

        # Detailed geometry
        self.__headerDepth = 20
        self.__statusbarDepth = 20
        self.__widgetDepth = (
            self._height - self.__headerDepth - self.__statusbarDepth
        )
        self._radius = self._width / 2 + self._dockHeight

        """
        =======================================================================
            Initialisation of backendstructure
        """
        self.__inputPipe = None
        self.hasOutput = False
        self.__path, self.__name = path, name
        self.__libs = libs
        self.__lastrun = 0
        self.__inittime, self.__runtime, self.__savetime = 0, 0, 0
        self.__testResults = {}

        self.__stdout = ""
        self.__status = "incomplete"
        self.__progress = 0
        self.__errorMessage = ""

        self.__pathChanged = PSSignal()
        self.__nameChanged = PSSignal()
        self.__stdoutChanged = PSSignal()
        self.__progressChanged = PSSignal()

        self.__worker = PSWorker(workerRegistrationFunction,
                                 startTimerFunction)
        self.worker.finished.connect(self.__finish)
        self.worker.newStdout.connect(self.addStdout)
        self.worker.progressUpdate.connect(self.updateProgress)

        """
        =======================================================================
            Initialise GUI module components:
                - Colored Header
                - Centralwidget with module name, run- and stop-button
                - Colored footer with statusbar
                - Docking slots for pipeline connection
        """

        # Header
        self.__header = PSModuleHeader(
            0, 0,
            self._width, self.__headerDepth,
            colors.get("standard-blue"), parent=self
        )

        self.__widget = PSModuleWidget(
            1, 0 + self.__headerDepth,
            self._width - 2,
            self._height - self.__headerDepth - self.__statusbarDepth,
            self.name, parent=self
        )

        def _nameChanged(name):
            self.name = name
        self.__widget.nameEdit.nameChanged.connect(_nameChanged)

        self.__widget.setPlayPauseButtonAction(self.__playPauseClicked)
        self.__widget.setStopButtonAction(self.__stopClicked)
        self.statusChanged.connect(self.__widget.updateIcons)

        self.__statusbar = PSModuleStatusbar(
            0,
            0 + self.__headerDepth + self.__widgetDepth,
            self._width, self.__statusbarDepth,
            colors.get("standard-blue"), parent=self
        )

        self.visualStatusUpdate(self)
        self.setCenterPos(QtCore.QPointF(x, y))

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

    def __lt__(a, b):
        return a.name < b.name

    def __gt__(a, b):
        return a.name > b.name

    def __getstate__(self) -> tuple:
        return (self.id, self.centerPos().x(), self.centerPos().y(), self.path,
                self.name, self.__libs)

    def __setstate__(self, state: tuple):
        self.__id, self.__path, self.__name = state[0], state[3], state[4]
        self.__libs = state[5]
        self.setPos(state[1], state[2])

    @property
    def saveProperties(self) -> dict:
        props = {"name": self.name,
                 "path": self.path,
                 "stdout": self.stdout,
                 "errorMessage": self.errorMessage,
                 "lastrun": self.lastrun,
                 "inittime": self.inittime,
                 "runtime": self.runtime,
                 "savetime": self.savetime,
                 "testResults": self.testResults,
                 "progress": self.progress
                 }
        props.update(super().saveProperties)

        if self.__inputPipe is not None:
            props["inPipeID"] = self.__inputPipe.id

        return props

    def restoreProperties(self, props: dict, stream: PSStream):
        super().restoreProperties(props, stream)
        if "stdout" in props:
            self.__stdout = props["stdout"]
        if "errorMessage" in props:
            self.__errorMessage = props["errorMessage"]
        if "lastrun" in props:
            self.__lastrun = props["lastrun"]
        if "inittime" in props:
            self.__inittime = props["inittime"]
        if "runtime" in props:
            self.__runtime = props["runtime"]
        if "testResults" in props:
            self.__testResults = props["testResults"]
        if "savetime" in props:
            self.__savetime = props["savetime"]
        if "progress" in props:
            self.updateProgress(props["progress"])

    @property
    def __shift(self) -> QtCore.QPointF:
        return QtCore.QPointF(self._width / 2, self._height / 2)

    @property
    def hasInput(self) -> bool:
        return self.__inputPipe is not None

    def centerPos(self) -> QtCore.QPoint:
        return self.pos() + self.__shift

    def setCenterPos(self, point: QtCore.QPoint):
        self.setPos(point - self.__shift)

    def __playPauseClicked(self):
        if self.status is PSStatus.RUNNING:
            self.pause()
        elif self.status is PSStatus.PAUSED:
            self.resume()
        else:
            self.run()

    def __stopClicked(self):
        self.stop()

    def visualStatusUpdate(self, module):
        if module == self:
            if self.status is PSStatus.ERROR:
                color = colors.get("error")
            elif self.status is PSStatus.TESTFAILED:
                color = colors.get("test-failed")
            elif self.status is PSStatus.RUNNING:
                color = colors.get("running")
            elif self.status is PSStatus.PAUSED:
                color = colors.get("paused")
            else:
                color = colors.get("standard-blue")

            self.__header.bgColor = color
            self.__statusbar.bgColor = color
            self.__statusbar.text = translate("Status", str(self.status))

    """
        properties
    """

    @property
    def path(self) -> str:
        return self.__path

    @path.setter
    def path(self, path: str):
        self.__path = path
        self.pathChanged.emit()

    @property
    def filePath(self) -> str:
        return self.__path + "/" + self.__name + ".py"

    @filePath.setter
    def filePath(self, path: str):
        basepath, name = os.path.split(path)

        if name[-3:] == ".py":
            name = name[:-3]
            if not os.path.exists(path):
                os.rename(self.filePath, path)
                self.__name = name
                self.__widget.nameEdit.setText(name)
                self.path = basepath
                self.nameChanged.emit(self)
            else:
                notificationsystem.newNotification(
                    translate("Module",
                              "A file with this name already exists. Please " +
                              "choose another name or delete the existing " +
                              "file."
                              )
                )

    def outsource(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName()

        if path != "":
            self.filePath = path

    def createModuleScript(self, text: str = None):
        with open(self.filePath, "w") as f:
            if text is None:
                f.write("\ndef main(stream):\n\treturn stream\n")
            else:
                f.write(text)

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str):
        if not os.path.exists(self.path + "/" + name + ".py"):
            os.rename(self.filePath, self.path + "/" + name + ".py")
            self.__name = name
            self.nameChanged.emit(self)
        else:
            notificationsystem.newNotification(
                translate("Module",
                          "A file with this name already exists. Please choose " +
                          "another name or delete the existing file."
                          )
            )
            self.__widget.nameEdit.setText(self.name)

    @property
    def worker(self) -> PSWorker:
        return self.__worker

    @property
    def stdout(self) -> str:
        return self.__stdout

    def resetStdout(self):
        self.__stdout = ""
        self.stdoutChanged.emit(self, None)

    def addStdout(self, value: str):
        self.__stdout += value
        self.stdoutChanged.emit(self, value)

    @property
    def errorMessage(self) -> str:
        return self.__errorMessage

    @property
    def progress(self) -> float:
        return self.__progress

    def updateProgress(self, value: float):
        self.__progress = value
        self.__widget.progressBar.show()
        self.__widget.progressBar.setValue(int(round(value * 100)))
        self.progressChanged.emit(self)

    @property
    def lastrun(self) -> float:
        return self.__lastrun

    @property
    def inittime(self) -> float:
        return self.__inittime

    @property
    def inittimeHHMMSS(self) -> str:
        m, s = divmod(self.__inittime, 60)
        h, m = divmod(m, 60)
        return "%02d:%02d:%02d.%003d" % (h, m, s, self.__inittime * 1000)

    @property
    def runtime(self) -> float:
        return self.__runtime

    @property
    def runtimeHHMMSS(self) -> str:
        m, s = divmod(self.__runtime, 60)
        h, m = divmod(m, 60)
        return "%02d:%02d:%02d.%003d" % (h, m, s, self.__runtime * 1000)

    @property
    def savetime(self) -> float:
        return self.__savetime

    @property
    def savetimeHHMMSS(self) -> str:
        m, s = divmod(self.__savetime, 60)
        h, m = divmod(m, 60)
        return "%02d:%02d:%02d.%003d" % (h, m, s, self.__savetime * 1000)

    @property
    def testResults(self) -> dict:
        return self.__testResults

    @property
    def statistics(self) -> str:
        text = translate("Module", "Last run") + ": " + \
            datetime.fromtimestamp(self.__lastrun).strftime(
                "%Y-%m-%d %H:%M:%S") + "<br>"
        text += translate("Module", "Run time") + \
            ": %s<br>" % (self.runtimeHHMMSS)
        text += translate("Module", "Save time") + \
            ": %d ms<br><br>" % (self.savetime * 1000)

        if len(self.testResults) > 0:
            text += translate("Module", "Test report") + ":<br>"

            for test in sorted(self.testResults):
                text += test + ": "
                if self.testResults[test]:
                    text += "<font color=\"green\">" + \
                        translate("Module", "SUCCESSFUL") + "</font><br>"
                else:
                    text += "<font color=\"red\">" + \
                        translate("Module", "FAILED") + "</font><br>"
        return text

    @property
    def pathChanged(self) -> PSSignal:
        return self.__pathChanged

    @property
    def nameChanged(self) -> PSSignal:
        return self.__nameChanged

    @property
    def stdoutChanged(self) -> PSSignal:
        return self.__stdoutChanged

    @property
    def progressChanged(self) -> PSSignal:
        return self.__progressChanged

    @property
    def header(self) -> PSModuleHeader:
        return self.__header

    """
        Connection stuff
    """

    @property
    def inputPipe(self):
        return self.__inputPipe

    @property
    def inputItems(self) -> list:
        if self.__inputPipe is None:
            return []
        return [self.__inputPipe]

    def establishConnection(self, otherItem: PSPuzzleItem,
                            silent: bool = False) -> QtCore.QPointF:
        self.__setInputPipe(otherItem)
        return super().establishConnection(otherItem)

    def removeConnection(self, otherItem):
        self.__disconnectInputPipe()
        super().removeConnection(otherItem)

    def __setInputPipe(self, pipe):
        self.__inputPipe = pipe
        self.__inputPipe.statusChanged.connect(self.inputUpdate)
        self.__inputPipe.hasOutput = True

    def __disconnectInputPipe(self):
        self.__inputPipe.statusChanged.disconnect(self.inputUpdate)
        self.__inputPipe.hasOutput = False
        self.__inputPipe = None

    """
    ===========================================================================
        Execution routines
    """

    def inputUpdate(self, pipe):
        if not pipe.stopHere:
            if pipe.status is PSStatus.FINISHED:
                self.run()
            if self.status not in (PSStatus.RUNNING, PSStatus.PAUSED):
                if pipe.status is PSStatus.WAITING:
                    self.status = PSStatus.WAITING
                else:
                    self.status = PSStatus.INCOMPLETE

    def run(self, stopHere: bool = False):
        if self.status is PSStatus.PAUSED:
            self.resume()
        elif self.status is not PSStatus.RUNNING:
            self.stopHere = stopHere

            self.resetStdout()

            self.__lastrun = time()
            if not self.hasInput:
                lastID = None
            else:
                self.streamSection = self.__inputPipe.streamSection.copy(
                    self.id)
                lastID = self.__inputPipe.id
            self.__inittime = time() - self.__lastrun

            self.worker.setName(self.name)
            self.worker.setPath(self.filePath)
            self.worker.setLibs(self.__libs)
            self.worker.enqueue(self.streamSection, self.id, lastID)
            self.updateProgress(0)
            self.status = PSStatus.RUNNING

    def pause(self):
        if self.status is PSStatus.RUNNING:
            if self.worker.pause():
                self.status = PSStatus.PAUSED

    def resume(self):
        if self.status is PSStatus.PAUSED:
            if self.worker.resume():
                self.status = PSStatus.RUNNING

    def stop(self):
        if self.status is PSStatus.RUNNING or self.status is PSStatus.PAUSED:
            if self.status is PSStatus.PAUSED:
                self.worker.resume()
            if self.worker.stop():
                self.status = PSStatus.INCOMPLETE

    def __finish(self, success: bool, log: list, out: str, times: list,
                 testResults: dict):
        self.__runtime, self.__savetime = times
        self.__testResults = testResults
        self.streamSection.changelog.update(log)

        if False in testResults.values():
            self.status = PSStatus.TESTFAILED
        elif success:
            self.status = PSStatus.FINISHED
            if self.__progress == 0:
                self.updateProgress(1)
        else:
            self.__errorMessage = out
            self.addStdout(out + "\n")
            self.status = PSStatus.ERROR
