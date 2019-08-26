# -*- coding: utf-8 -*-
"""Main window module.

contains PSMainWindow, a subclass of QMainWindow
"""

import gc
import importlib
import inspect
import json
import os
import shutil
import subprocess
import sys
import time
import webbrowser
import zipfile
from distutils.version import LooseVersion
from threading import Thread
from typing import Callable
from urllib.request import urlopen

import pkg_resources
import puzzlestream.ui.resources as resources
from appdirs import user_config_dir
from puzzlestream.backend import notificationsystem
from puzzlestream.backend.status import PSStatus
from puzzlestream.ui import colors
from puzzlestream.ui.about import PSAboutWindow
from puzzlestream.ui.codeeditor import PSCodeEdit
from puzzlestream.ui.dataview import PSDataView
from puzzlestream.ui.editorwidget import PSEditorWidget
from puzzlestream.ui.gittab import PSGitTab
from puzzlestream.ui.graphicsview import PSGraphicsView
from puzzlestream.ui.manager import PSManager
from puzzlestream.ui.module import PSModule
from puzzlestream.ui.notificationtab import PSNotificationTab
from puzzlestream.ui.outputtextedit import PSOutputTextEdit
from puzzlestream.ui.pip import PSPipGUI
from puzzlestream.ui.pipe import PSPipe
from puzzlestream.ui.plotview import PSPlotView
from puzzlestream.ui.preferences import PSPreferencesWindow
from puzzlestream.ui.puzzleitem import PSPuzzleItem
from puzzlestream.ui.switch import PSSlideSwitch
from puzzlestream.ui.translate import changeLanguage
from pyqode.python.backend import server
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

translate = QCoreApplication.translate


class PSMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.__manager = PSManager(self)
        self.__manager.configChanged.connect(self.__configChanged)
        self.__manager.scene.nameChanged.connect(self.__nameChanged)
        self.__manager.scene.itemDeleted.connect(self.__itemDeleted)

        self.setupUi()
        self.__activeModule = None
        self.__subWindows = []
        self.puzzleGraphicsView.setScene(self.__manager.scene)
        self.puzzleGraphicsView.setConfig(self.__manager.config)

        currentDir = os.path.dirname(__file__)
        self.setWindowIcon(QIcon(
            os.path.join(currentDir, "../icons//Puzzlestream.png")))

        # editor initialisation
        w = self.__newEditorWidget()
        self.__editorWidgets = [w]
        self.__editors = [w.editor]
        w.moduleFileOpened.connect(self.__updateActiveModuleFromFileExplorer)
        self.horizontalSplitter.insertWidget(0, w)
        self.btnOpenCloseSecondEditor = QPushButton(self)
        self.btnOpenCloseSecondEditor.setText("+")
        self.__editorWidgets[0].editorHeaderLayout.addWidget(
            self.btnOpenCloseSecondEditor)
        self.btnOpenCloseSecondEditor.setStyleSheet(
            "QPushButton { min-width: 1em; max-width: 1em; " +
            "min-height: 1em; max-height: 1em; }"
        )
        self.btnOpenCloseSecondEditor.clicked.connect(
            lambda: self.changeRightWidgetMode("editor"))
        self.__rightWidget = self.verticalSplitter
        self.__rightWidgetMode = "puzzle"

        # add active module run / pause / stop
        self.btnRunPauseActive = QToolButton()
        self.btnRunPauseActive.clicked.connect(self.__runPauseActiveModuleOnly)
        self.btnStopActive = QToolButton()
        self.btnStopActive.clicked.connect(self.__stopActiveModule)
        w.editorHeaderLayout.insertWidget(0, self.btnRunPauseActive)
        w.editorHeaderLayout.insertWidget(1, self.btnStopActive)

        # pre-add second editor for windows performance reasons
        w = self.__newEditorWidget()
        self.__editorWidgets.append(w)
        self.__editors.append(w.editor)

        # welcome screen
        self.__welcomeLabel = QLabel(self)
        font = QFont()
        font.setPointSize(16)
        self.__welcomeLabel.setFont(font)
        self.__welcomeLabel.setTextFormat(Qt.RichText)
        self.__welcomeLabel.setAlignment(Qt.AlignCenter)
        self.__welcomeLabel.setContentsMargins(5, 0, 5, 0)
        self.__welcomeLabel.linkActivated.connect(
            self.__welcomeLabelLinkActivated)
        self.horizontalSplitter.insertWidget(
            0, self.__welcomeLabel)

        self.horizontalSplitter.setStretchFactor(0, 1)
        self.horizontalSplitter.setStretchFactor(1, 6)
        self.horizontalSplitter.setStretchFactor(2, 3)
        self.horizontalSplitter.setCollapsible(0, True)
        self.horizontalSplitter.setCollapsible(1, True)

        self.verticalSplitter.setStretchFactor(0, 10)
        self.verticalSplitter.setStretchFactor(1, 1)
        self.verticalSplitter.setCollapsible(1, True)

        # create puzzle toolbar actions
        self.__createPuzzleToolBarActions()
        for action in self.__getPuzzleToolBarActions():
            self.puzzleToolBar.addAction(action)

        self.__btnAddStatusAbort = QPushButton(self.startToolBar)
        self.__btnAddStatusAbort.clicked.connect(self.__abortAdding)
        self.__btnAddStatusAction = self.puzzleToolBar.addWidget(
            self.__btnAddStatusAbort)
        self.__btnAddStatusAction.setVisible(False)
        self.__puzzleLabel = QLabel(self.puzzleToolBar)
        self.puzzleToolBar.addWidget(self.__puzzleLabel)

        self.__lblPuzzleLock = QLabel()
        self.__btnPuzzleLock = PSSlideSwitch()
        self.__btnPuzzleLock.setSizePolicy(QSizePolicy.Fixed,
                                           QSizePolicy.Fixed)
        self.__btnPuzzleLock.setStyleSheet(
            "* { min-width: 2.2em; max-width: 2.2em; " +
            "min-height: 1.3em; max-height: 1.3em; }"
        )
        self.__btnPuzzleLock.toggled.connect(self.__togglePuzzleLocked)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding,
                             QSizePolicy.Expanding)
        spacer2 = QWidget()
        spacer2.setSizePolicy(QSizePolicy.Fixed,
                              QSizePolicy.Expanding)
        spacer2.setStyleSheet(
            "QWidget { min-width: 0.2em; max-width: 0.2em; }")

        self.puzzleToolBar.addWidget(spacer)
        self.puzzleToolBar.addWidget(self.__lblPuzzleLock)
        self.puzzleToolBar.addWidget(spacer2)
        self.puzzleToolBar.addWidget(self.__btnPuzzleLock)

        # create menu bar
        self.__createLeftCornerToolbarActions()
        self.__createRightCornerToolbarActions()
        self.__createStartToolBarActions()
        self.__createEditToolBarActions()
        self.__createAppsToolBarActions()
        self.__createStreamToolBarActions()
        self.__createHelpToolBarActions()
        self.__updateRecentProjects()
        self.__createLibToolBarActions()

        # create graphics scene
        self.__createGraphicsScene()

        # set active module to None
        self.__resetActiveModule()

        # set style
        self.__currentStyle = None
        design = self.__manager.config["design"]
        self.__setStyle(design[1][design[0]])

        # shortcuts
        self.__shortcuts = {}
        self.addShortcut("F5", self.__runPauseActiveModuleOnly)
        self.addShortcut("Alt+F5", self.__runPauseActiveModule)
        self.addShortcut("Ctrl+F5", self.__run)
        self.addShortcut("F11", self.__toggleFullscreen)
        self.addShortcut("Ctrl+s", self.__saveOpenFiles)
        self.addShortcut("Esc", self.__abortAdding)

        # git
        self.__gitTab = PSGitTab(self.outputTabWidget)
        self.outputTabWidget.addTab(self.__gitTab, "Git")
        self.__manager.updateSignal.connect(self.__gitTab.reload)
        self.__gitTab.reloadSignal.connect(self.__updateGitTabHeaderAndMenu)
        self.__gitTab.fileSaveSignal.connect(self.__saveOpenFiles)
        self.__gitTab.fileUpdateSignal.connect(self.__reloadAllEditors)
        self.__createGitToolBarActions()

        # notifications
        self.__notificationTab = PSNotificationTab(
            self.outputTabWidget)
        self.outputTabWidget.addTab(self.__notificationTab,
                                    "Notifications (0)")
        notificationsystem.addReactionMethod(
            self.__notificationTab.addNotification,
            throwArchived=True
        )
        self.__notificationTab.setNumberUpdateMethod(
            self.__updateNotificationHeader)

        # collect elements that should be activated and deactivated
        self.__activeElements = [
            self.puzzleGraphicsView, self.__newModuleMenu,
            self.__newPipeAction, self.__newValveAction, self.__undoAction,
            self.__redoAction, self.__copyAction, self.__cutAction,
            self.__pasteAction, self.__runAction, self.__pauseAction,
            self.__stopAction, self.__btnPuzzleLock
        ]

        """
        =======================================================================
            Start update check
        """
        thr = Thread(target=self.__checkForUpdates)
        thr.start()
        self.__updateCheckTimer = QTimer()
        self.__updateCheckTimer.singleShot(5000, self.__updateCheckFinished)

        """
        =======================================================================
            Show window
        """

        self.retranslateUi()
        self.resize(1200, 800)
        self.showMaximized()
        self.__lastWindowState = "maximized"

    @property
    def __newProjectText(self) -> str:
        color = colors.get("standard-blue")
        text = translate(
            "MainWindow",
            "<img src=\":/Puzzlestream.png\" width=\"128\" height=\"128\">" +
            "<p>You may <a href=\"#new_project\">"
            "<span style=\"color: #177dc9;\">create a new project " +
            "folder</span></a> or <a href=\"#open_project\">"
            "<span style=\"color: #177dc9;\">open an existing " +
            "project</span></a><br>and start working.</p><br><p>" +
            "<font size=\"-1\">Last projects:</font></p>"
        )
        for item in self.__manager.config["last projects"][::-1]:
            text += "<a href=\"#last_project:"
            text += "%s\"><span style=\"color: %s;\">" % (item, color)
            text += "<font size=\"-2\">%s" % (item)
            text += "</font></span></a><br>"
        return text

    @property
    def __projectOpenText(self) -> str:
        return translate(
            "MainWindow",
            "Add a new module or select an existing one<br>to edit its " +
            "source code."
        )

    @property
    def __newItemText(self) -> str:
        return translate(
            "MainWindow",
            "Click left on the scrollable puzzle region to add a "
        )

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.centralGrid = QWidget(self)
        self.centralGrid.setObjectName("centralGrid")
        self.gridLayout = QGridLayout(self.centralGrid)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalSplitter = QSplitter(self.centralGrid)
        self.horizontalSplitter.setOrientation(Qt.Horizontal)
        self.horizontalSplitter.setObjectName("horizontalSplitter")
        self.verticalSplitter = QSplitter(self.horizontalSplitter)
        self.verticalSplitter.setOrientation(Qt.Vertical)
        self.verticalSplitter.setObjectName("verticalSplitter")
        self.verticalSplitter.setContentsMargins(0, 0, 0, 0)
        self.puzzleWidget = QWidget(self.verticalSplitter)
        self.puzzleWidget.setObjectName("puzzleWidget")
        self.puzzleWidgetLayout = QVBoxLayout()
        self.puzzleWidget.setLayout(self.puzzleWidgetLayout)
        self.puzzleWidgetLayout.setContentsMargins(0, 0, 0, 0)
        self.puzzleGraphicsView = PSGraphicsView(self.__manager,
                                                 self.puzzleWidget)
        self.puzzleGraphicsView.focusIn.connect(self.__puzzleFocusIn)
        self.puzzleGraphicsView.setObjectName("puzzleGraphicsView")
        self.puzzleWidgetLayout.addWidget(self.puzzleGraphicsView)
        self.outputTabWidget = QTabWidget(self.verticalSplitter)
        self.outputTabWidget.setObjectName("outputTabWidget")
        self.textTab = QWidget()
        self.textTab.setObjectName("textTab")
        self.textTabGridLayout = QGridLayout(self.textTab)
        self.textTabGridLayout.setObjectName("textTabGridLayout")
        self.outputTextEdit = PSOutputTextEdit(self.textTab)
        self.outputTextEdit.setObjectName("outputTextEdit")
        self.textTabGridLayout.addWidget(self.outputTextEdit, 0, 0, 1, 1)
        self.outputTabWidget.addTab(self.textTab, "")
        self.statisticsTab = QWidget()
        self.statisticsTab.setObjectName("statisticsTab")
        self.statisticsTabGridLayout = QGridLayout(
            self.statisticsTab)
        self.statisticsTabGridLayout.setObjectName("statisticsTabGridLayout")
        self.vertPlotTabLayout = QVBoxLayout()
        self.vertPlotTabLayout.setObjectName("vertPlotTabLayout")
        self.horPlotSelComboBoxLayout = QHBoxLayout()
        self.horPlotSelComboBoxLayout.setObjectName("horPlotSelComboBoxLayout")
        self.vertPlotTabLayout.addLayout(self.horPlotSelComboBoxLayout)
        self.statisticsTabGridLayout.addLayout(
            self.vertPlotTabLayout, 0, 0, 1, 1)
        self.outputTabWidget.addTab(self.statisticsTab, "")
        self.statisticsTextEdit = QTextEdit(self.statisticsTab)
        self.statisticsTextEdit.setReadOnly(True)
        self.statisticsTextEdit.setObjectName("statisticsTextEdit")
        self.statisticsTabGridLayout.addWidget(self.statisticsTextEdit,
                                               0, 0, 1, 1)
        self.gridLayout.addWidget(self.horizontalSplitter, 1, 1)
        self.setCentralWidget(self.centralGrid)
        self.mainTabWidget = QTabWidget()
        self.mainTabWidget.setSizePolicy(QSizePolicy.Expanding,
                                         QSizePolicy.Fixed)
        self.mainTabWidget.tabBar().setObjectName("mainTabBar")
        self.startToolBar = QToolBar(self)
        self.startToolBar.setObjectName("startToolBar")
        self.startToolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.mainTabWidget.addTab(self.startToolBar, "Start")
        self.editToolBar = QToolBar(self)
        self.editToolBar.setObjectName("editToolBar")
        self.editToolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.mainTabWidget.addTab(self.editToolBar, "Edit")
        self.puzzleToolBar = QToolBar(self)
        self.puzzleToolBar.setObjectName("puzzleToolBar")
        self.puzzleToolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.mainTabWidget.addTab(self.puzzleToolBar, "Puzzle")
        self.appsToolBar = QToolBar(self)
        self.appsToolBar.setObjectName("appsToolBar")
        self.appsToolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.mainTabWidget.addTab(self.appsToolBar, "Apps")
        self.libToolBar = QToolBar(self)
        self.libToolBar.setObjectName("libToolBar")
        self.libToolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.mainTabWidget.addTab(self.libToolBar, "Libraries")
        self.streamToolBar = QToolBar(self)
        self.streamToolBar.setObjectName("streamToolBar")
        self.streamToolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.mainTabWidget.addTab(self.streamToolBar, "Stream")
        self.gitToolBar = QToolBar(self)
        self.gitToolBar.setObjectName("gitToolBar")
        self.gitToolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.mainTabWidget.addTab(self.gitToolBar, "Git")
        self.helpToolBar = QToolBar(self)
        self.helpToolBar.setObjectName("helpToolBar")
        self.helpToolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.mainTabWidget.addTab(self.helpToolBar, "Help")
        self.gridLayout.addWidget(self.mainTabWidget, 0, 0, 1, 2)

        self.leftCornerToolBar = QToolBar(self)
        self.leftCornerToolBar.setObjectName("leftCornerToolBar")
        self.mainTabWidget.setCornerWidget(self.leftCornerToolBar,
                                           Qt.TopLeftCorner)

        self.rightCornerToolBar = QToolBar(self)
        self.rightCornerToolBar.setObjectName("rightCornerToolBar")
        self.mainTabWidget.setCornerWidget(self.rightCornerToolBar,
                                           Qt.TopRightCorner)

    def retranslateUi(self):
        self.setWindowTitle(translate("MainWindow", "Puzzlestream"))
        self.__updateProjectLoadedStatus()
        self.outputTabWidget.setTabText(
            self.outputTabWidget.indexOf(self.textTab), translate(
                "MainWindow", "Output"))
        self.outputTabWidget.setTabText(
            self.outputTabWidget.indexOf(self.statisticsTab), translate(
                "MainWindow", "Statistics"))
        self.mainTabWidget.setTabText(0, translate("MainWindow", "Start"))
        self.mainTabWidget.setTabText(1, translate("MainWindow", "Edit"))
        self.mainTabWidget.setTabText(2, translate("MainWindow", "Puzzle"))
        self.mainTabWidget.setTabText(3, translate("MainWindow", "Apps"))
        self.mainTabWidget.setTabText(4, translate("MainWindow", "Libraries"))
        self.mainTabWidget.setTabText(5, translate("MainWindow", "Stream"))
        self.mainTabWidget.setTabText(6, translate("MainWindow", "Git"))
        self.mainTabWidget.setTabText(7, translate("MainWindow", "Help"))

        self.btnOpenCloseSecondEditor.setToolTip("Open second editor")
        self.btnRunPauseActive.setToolTip("Run current module")
        self.btnStopActive.setToolTip("Stop current module")
        self.__btnAddStatusAbort.setText(translate("MainWindow", "Abort"))

        self.__dataToolbarAction.setText(translate("MainWindow", "Show &data"))
        self.__plotToolbarAction.setText(
            translate("MainWindow", "Show &plots"))
        self.__cleanToolbarAction.setText(
            translate("MainWindow", "&Clean stream"))

        self.__createLibToolBarActions()

        self.__fetchToolbarAction.setText(
            translate("MainWindow", "&Fetch / reload"))
        self.__pullToolbarAction.setText(translate("MainWindow", "Pull"))
        self.__pushToolbarAction.setText(translate("MainWindow", "Push"))

        self.__preferencesToolbarAction.setText(
            translate("MainWindow", "Pre&ferences"))
        self.__userGuideToolbarAction.setText(
            translate("MainWindow", "&User guide"))
        self.__aboutToolbarAction.setText(
            translate("MainWindow", "&About Puzzlestream"))
        self.__websiteToolbarAction.setText(
            translate("MainWindow", "&Puzzlestream website"))
        self.__debugToolbarAction.setText(
            translate("MainWindow", "&Save debug information"))

        self.__newModuleMenu.setTitle(translate("MainWindow", "New module"))
        self.__newIntModuleAction.setText(
            translate("MainWindow", "New internal module"))
        self.__newExtModuleAction.setText(
            translate("MainWindow", "New external module"))
        self.__newTemplateModuleMenu.setTitle(
            translate("MainWindow", "From template"))
        self.__newPipeAction.setText(translate("MainWindow", "New pipe"))
        self.__newValveAction.setText(translate("MainWindow", "New valve"))

        self.__createGraphicsSceneContextMenu()
        self.btnOpenCloseSecondEditor.setToolTip(
            translate("MainWindow", "Open second editor"))

        if self.__activeModule is not None:
            self.__updateActiveModule(self.__activeModule)
        self.__updateNotificationHeader()

        for m in self.__manager.scene.modules.values():
            m.visualStatusUpdate(m)

        self.__newProjectAction.setText(
            translate("MainWindow", "New project"))
        self.__openProjectAction.setText(
            translate("MainWindow", "Open project"))
        self.__saveProjectAsAction.setText(
            translate("MainWindow", "&Save project as..."))
        self.__recentProjectsMenu.setTitle(
            translate("MainWindow", "&Recent projects"))
        self.__closeProjectAction.setText(
            translate("MainWindow", "&Close project"))
        self.__saveFileAction.setText(translate("MainWindow", "Save file"))
        self.__undoAction.setText(translate("MainWindow", "Back"))
        self.__redoAction.setText(translate("MainWindow", "Forward"))
        self.__copyAction.setText(translate("MainWindow", "Copy"))
        self.__cutAction.setText(translate("MainWindow", "Cut"))
        self.__pasteAction.setText(translate("MainWindow", "Paste"))
        self.__autoformatToolbarAction.setText(
            translate("MainWindow", "&Format code"))
        self.__sortImportsToolbarAction.setText(
            translate("MainWindow", "&Sort imports"))
        self.__runAction.setText(translate("MainWindow", "Run puzzle"))
        self.__pauseAction.setText(translate("MainWindow", "Pause puzzle"))
        self.__stopAction.setText(translate("MainWindow", "Stop puzzle"))
        self.__puzzleViewAction.setText(translate("MainWindow", "Puzzle"))
        self.__dataViewAction.setText(translate("MainWindow", "Data view"))
        self.__plotViewAction.setText(translate("MainWindow", "Plot view"))

        self.__togglePuzzleLocked()

    def changeEvent(self, event: QEvent):
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        return super().changeEvent(event)

    def __setStyle(self, style: str):
        self.__currentStyle = style
        currentDir = os.path.dirname(__file__)
        colors.update(os.path.join(currentDir, "style/" + style + ".yml"))
        self.setStyleSheet(
            colors.parseQSS(currentDir + "/style/sheet-em.qss"))
        for e in self.__editors:
            e.setSyntaxColorScheme(style)

        for w in self.__subWindows:
            w.setStyleSheet(
                colors.parseQSS(currentDir + "/style/sheet-em.qss"))

        if style == "dark":
            self.__newProjectAction.setIcon(
                QIcon(os.path.join(currentDir,
                                   "../icons//new_project_white.png")))
            self.__openProjectAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//folder_white.png")))
            self.__saveFileAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//save_blue_in.png")))
            self.__undoAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//back_white.png")))
            self.__redoAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//forward_white.png")))
            self.__copyAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//copy_blue_in.png")))
            self.__cutAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//cut_blue_in.png")))
            self.__pasteAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//paste_blue_in.png")))
            self.__runAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons/play_blue_in.png")))
            self.__pauseAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons/pause_blue_in.png")))
            self.__stopAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//stop_blue_in.png")))
            self.btnStopActive.setIcon(
                QIcon(os.path.join(currentDir, "../icons//stop_blue_in.png")))
        elif style == "light":
            self.__newProjectAction.setIcon(
                QIcon(os.path.join(currentDir,
                                   "../icons//new_project_blue.png")))
            self.__openProjectAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//folder_blue.png")))
            self.__saveFileAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//save_blue_out.png")))
            self.__undoAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//back_blue.png")))
            self.__redoAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//forward_blue.png")))
            self.__copyAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//copy_blue_out.png")))
            self.__cutAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//cut_blue_out.png")))
            self.__pasteAction.setIcon(
                QIcon(os.path.join(currentDir,
                                   "../icons//paste_blue_out.png")))
            self.__runAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons/play_blue_out.png")))
            self.__pauseAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons/pause_blue_out.png")))
            self.__stopAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//stop_blue_out.png")))
            self.btnStopActive.setIcon(
                QIcon(os.path.join(currentDir, "../icons//stop_blue_out.png")))

        self.updateActiveModuleButtons()

        color = colors.get("corner-toolbar")
        self.rightCornerToolBar.widgetForAction(self.__puzzleViewAction).setStyleSheet(
            "QToolButton { background-color: %s; }" % (color))
        self.rightCornerToolBar.widgetForAction(self.__dataViewAction).setStyleSheet(
            "QToolButton { background-color: %s; }" % (color))
        self.rightCornerToolBar.widgetForAction(self.__plotViewAction).setStyleSheet(
            "QToolButton { background-color: %s; }" % (color))

        titleBarColor = colors.get("Qt-title-bar-background")
        self.leftCornerToolBar.setStyleSheet(
            "QWidget { background-color: %s; }" % (titleBarColor))
        self.rightCornerToolBar.setStyleSheet(
            "QWidget { background-color: %s; }" % (titleBarColor))
        self.centralGrid.setStyleSheet(
            "QWidget#centralGrid { background-color: %s; }" % (titleBarColor))
        self.mainTabWidget.setStyleSheet(
            "QTabBar { background-color: %s; }" % (titleBarColor))
        self.gridLayout.setSpacing(0)
        self.__manager.scene.setBackgroundBrush(
            QBrush(QColor(colors.get("Qt-graphicsscene-background"))))

    def __autoformatFirstEditor(self):
        self.__editors[0].autoformat()

    def __sortImportsInFirstEditor(self):
        self.__editors[0].sortImports()

    def __saveOpenFiles(self):
        for e in self.__editors:
            if self.__manager.config["autoformatOnSave"]:
                e.autoformat()
            e.file.save()
        self.__fileDirty(False)
        self.__gitTab.reload()

    def __closeOpenFiles(self):
        for e in self.__editors:
            e.file.close()

    def __reloadAllEditors(self):
        for e in self.__editors:
            if e.file.path != "":
                e.file.reload(e.file.encoding)

    def __stopAllEditors(self):
        for e in self.__editors:
            e.backend.stop()

    def __autoformatAllEditors(self):
        for e in self.__editors:
            e.autoformat()

    def __sortImportsInAllEditors(self):
        for e in self.__editors:
            e.sortImports()

    def __newEditorWidget(self) -> PSEditorWidget:
        e = PSEditorWidget()
        design = self.__manager.config["design"]
        e.editor.setSyntaxColorScheme(design[1][design[0]])

        # editor settings
        e.editor.save_on_focus_out = self.__manager.config[
            "saveOnEditorFocusOut"]
        e.editor.replace_tabs_by_spaces = True
        e.editor.dirty_changed.connect(self.__fileDirty)
        e.editor.textChanged.connect(
            lambda: self.__editorTextChanged(e.editor))
        e.editor.focusIn.connect(self.__editorFocusIn)
        return e

    def __editorFocusIn(self):
        self.mainTabWidget.setCurrentIndex(1)

    def __puzzleFocusIn(self):
        self.mainTabWidget.setCurrentIndex(2)

    def openPuzzle(self):
        self.verticalSplitter.show()
        self.__enableAddActions()
        self.__rightWidget = self.verticalSplitter

    def closePuzzle(self):
        self.verticalSplitter.hide()
        self.__disableAddActions()
        self.__rightWidget = None

    def openSecondEditor(self, oldMode: str = "puzzle"):
        w = self.__editorWidgets[1]
        self.horizontalSplitter.insertWidget(2, w)
        i = self.horizontalSplitter.indexOf(
            self.verticalSplitter)
        self.__updateEditorModule(self.__activeModule, 1)
        self.btnOpenCloseSecondEditor.setText("-")
        self.btnOpenCloseSecondEditor.clicked.disconnect()
        self.btnOpenCloseSecondEditor.setToolTip(
            translate("MainWindow", "Close second editor"))
        self.btnOpenCloseSecondEditor.clicked.connect(
            lambda: self.changeRightWidgetMode(oldMode))
        self.__rightWidget = w
        self.__rightWidgetMode = "editor"
        self.__rightWidget.show()

    def closeSecondEditor(self):
        w = self.__editorWidgets[1]
        w.editor.file.save()
        w.hide()
        w.setParent(None)
        self.btnOpenCloseSecondEditor.setText("+")
        self.btnOpenCloseSecondEditor.clicked.disconnect()
        self.btnOpenCloseSecondEditor.clicked.connect(
            lambda: self.changeRightWidgetMode("editor"))
        self.__rightWidget = None

    def openDataview(self):
        w = PSDataView(self.__manager, self.__activeModule, self)
        self.__manager.scene.statusChanged.connect(w.statusUpdate)
        self.horizontalSplitter.insertWidget(2, w)
        self.__rightWidget = w
        self.__rightWidgetMode = "dataview"

    def closeDataview(self):
        self.__rightWidget.close()
        self.__rightWidget.hide()
        self.__rightWidget.setParent(None)
        del self.__rightWidget
        self.__rightWidget = None

    def openPlotview(self):
        w = PSPlotView(self.__manager, self.__activeModule, self)
        self.__manager.scene.statusChanged.connect(w.statusUpdate)
        self.horizontalSplitter.insertWidget(2, w)
        self.__rightWidget = w
        self.__rightWidgetMode = "dataview"

    def closePlotview(self):
        self.__rightWidget.close()
        self.__rightWidget.hide()
        self.__rightWidget.setParent(None)
        del self.__rightWidget
        self.__rightWidget = None

    def changeRightWidgetMode(self, mode: str):
        if mode != self.__rightWidgetMode:
            self.__manager.addStatus = None
            self.__puzzleLabel.setText("")
            self.__btnAddStatusAction.setVisible(False)
            s = self.horizontalSplitter.sizes()

            # close old mode
            if self.__rightWidgetMode == "editor":
                self.closeSecondEditor()
            elif self.__rightWidgetMode == "puzzle":
                self.closePuzzle()
            elif self.__rightWidgetMode == "dataview":
                self.closeDataview()
            elif self.__rightWidgetMode == "plotview":
                self.closePlotview()

            # choose new mode
            if mode == "editor":
                self.openSecondEditor(self.__rightWidgetMode)
                for w in [self.__puzzleViewAction, self.__dataViewAction,
                          self.__plotViewAction]:
                    w.setEnabled(True)
            elif mode == "puzzle":
                self.openPuzzle()
                for w in [self.__dataViewAction, self.__plotViewAction]:
                    w.setEnabled(True)
                self.__puzzleViewAction.setEnabled(False)
            elif mode == "dataview":
                self.openDataview()
                for w in [self.__puzzleViewAction, self.__plotViewAction]:
                    w.setEnabled(True)
                self.__dataViewAction.setEnabled(False)
            elif mode == "plotview":
                self.openPlotview()
                for w in [self.__puzzleViewAction, self.__dataViewAction]:
                    w.setEnabled(True)
                self.__plotViewAction.setEnabled(False)

            self.__rightWidgetMode = mode

            # restore sizes
            if len(self.horizontalSplitter.sizes()) == 3:
                self.horizontalSplitter.setSizes(
                    [0, s[1], sum(s) - s[1]])
            else:
                self.horizontalSplitter.setSizes(
                    [0, s[1], sum(s) - s[1], 0])

    def __editorTextChanged(self, editor: PSCodeEdit):
        if editor.hasFocus():
            for e in self.__editors:
                if e != editor and e.file.path == editor.file.path:
                    e.setPlainText(editor.toPlainText())

    def closeEvent(self, event: QEvent):
        if self.__manager.projectPath is not None:
            self.__manager.stopAllWorkers()
            self.__manager.save(thread=False)
            self.__manager.close()

        self.__saveOpenFiles()
        self.__closeOpenFiles()
        self.__stopAllEditors()
        event.accept()

    def __resetUI(self, path: str):
        self.__editorWidgets[0].hide()
        self.outputTextEdit.setText("")
        self.statisticsTextEdit.setText("")

    def __createGraphicsScene(self):
        scene = self.__manager.scene
        scene.stdoutChanged.connect(self.updateText)
        scene.statusChanged.connect(self.updateStatus)
        scene.itemAdded.connect(self.__itemAdded)
        scene.dataViewRequested.connect(self.__showData)
        scene.plotViewRequested.connect(self.__showPlots)
        scene.selectionChanged.connect(self.__selectionChanged)

    def __createGraphicsSceneContextMenu(self):
        menu = QMenu()
        newModuleMenu = menu.addMenu(
            translate("MainWindow", "New module"))
        newInternalModuleAction = newModuleMenu.addAction(
            translate("MainWindow", "New internal module"))
        newExternalModuleAction = newModuleMenu.addAction(
            translate("MainWindow", "New external module"))
        newTemplateModuleMenu = newModuleMenu.addMenu(
            translate("MainWindow", "From template"))
        newPipeAction = menu.addAction(translate("MainWindow", "New pipe"))
        newValveAction = menu.addAction(translate("MainWindow", "New valve"))

        for a in self.__getTemplateActions():
            action = newTemplateModuleMenu.addAction(a)
            action.triggered.connect(
                lambda _, p=a: self.__newIntModuleFromTemplate(templatePath=p))
        action = newTemplateModuleMenu.addAction(
            translate("MainWindow", "-> Manage templates"))
        path = os.path.join(user_config_dir("Puzzlestream"), "templates")
        action.triggered.connect(lambda _, p=path: self.__open_file(p))

        newModuleMenu.menuAction().triggered.connect(self.__newIntModule)
        newInternalModuleAction.triggered.connect(self.__newIntModule)
        newExternalModuleAction.triggered.connect(self.__newExtModule)
        newPipeAction.triggered.connect(self.__newPipe)
        newValveAction.triggered.connect(self.__newValve)

        self.__manager.scene.setStandardContextMenu(menu)

    def addShortcut(self, sequence: str, target: Callable):
        sc = QShortcut(QKeySequence(sequence), self)
        sc.activated.connect(target)
        self.__shortcuts[sequence] = sc

    def __selectionChanged(self):
        if len(self.__manager.scene.selectedItemList) == 1:
            puzzleItem = self.__manager.scene.selectedItemList[0]
            if isinstance(puzzleItem, PSModule):
                self.__updateActiveModule(puzzleItem)

    def __updateActiveModule(self, module: PSModule):
        self.__updateEditorModule(module)
        self.__activeModule = module
        for a in self.appsToolBar.actions():
            a.setEnabled(self.__activeModule is not None)
        self.outputTextEdit.setText(module.stdout)
        cursor = self.outputTextEdit.textCursor()
        cursor.movePosition(cursor.End)
        self.outputTextEdit.setTextCursor(cursor)
        self.outputTextEdit.ensureCursorVisible()
        self.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
        self.statisticsTextEdit.setHtml(module.statistics)
        self.outputTabWidget.setTabText(
            0, translate("MainWindow", "Output") + " - " + module.name)
        self.outputTabWidget.setTabText(
            1, translate("MainWindow", "Statistics") + " - " + module.name)
        self.__welcomeLabel.hide()
        self.__editorWidgets[0].show()
        self.updateActiveModuleButtons()

        for a in [self.__plotViewAction, self.__dataViewAction]:
            a.setEnabled(True)

        if self.__rightWidgetMode in ["dataview", "plotview"]:
            self.__rightWidget.updatePuzzleItem(module)

    def __updateActiveModuleFromFileExplorer(self, module: PSModule):
        self.__updateActiveModule(module)
        scene = self.__manager.scene
        scene.selectionChanged.disconnect(self.__selectionChanged)
        scene.clearSelection()
        module.setSelected(True)
        scene.selectionChanged.connect(self.__selectionChanged)

    def __updateEditorModule(self, module: PSModule, i: int = 0):
        if not os.path.exists(module.filePath):
            module.createModuleScript()
        self.__updateEditorModuleList()
        self.__editorWidgets[i].openModule(module)

    def __updateEditorModuleList(self):
        for e in self.__editorWidgets:
            e.setModules(self.__manager.scene.modules.values())

    def __runPauseActiveModule(self, stopHere: bool = False):
        if self.__activeModule is not None:
            if self.__manager.config["saveOnRun"]:
                self.__saveOpenFiles()

            if (self.__activeModule.status in
                    [PSStatus.INCOMPLETE, PSStatus.FINISHED, PSStatus.ERROR]):
                self.__activeModule.run(stopHere=stopHere)
            elif self.__activeModule.status is PSStatus.PAUSED:
                self.__activeModule.resume()
            elif self.__activeModule.status is PSStatus.RUNNING:
                self.__activeModule.pause()

    def __runPauseActiveModuleOnly(self):
        self.__runPauseActiveModule(stopHere=True)

    def __stopActiveModule(self):
        self.__activeModule.stop()

    def __nameChanged(self, module: PSModule):
        if module == self.__activeModule:
            self.__updateActiveModule(module)

    def __fileDirty(self, dirty: bool):
        self.__saveFileAction.setEnabled(dirty)

    def __createLeftCornerToolbarActions(self):
        self.__saveFileAction = self.leftCornerToolBar.addAction("")
        self.__saveFileAction.setEnabled(False)
        self.__saveFileAction.triggered.connect(self.__saveFileToolbar)

    def __createRightCornerToolbarActions(self):
        self.__puzzleViewAction = self.rightCornerToolBar.addAction("")
        self.__dataViewAction = self.rightCornerToolBar.addAction("")
        self.__plotViewAction = self.rightCornerToolBar.addAction("")

        for a in [self.__puzzleViewAction, self.__dataViewAction,
                  self.__plotViewAction]:
            a.setEnabled(False)

        self.__puzzleViewAction.triggered.connect(
            lambda: self.changeRightWidgetMode("puzzle"))
        self.__dataViewAction.triggered.connect(
            lambda: self.changeRightWidgetMode("dataview"))
        self.__plotViewAction.triggered.connect(
            lambda: self.changeRightWidgetMode("plotview"))

    def __createStartToolBarActions(self):
        self.__newProjectAction = self.startToolBar.addAction("")
        self.__openProjectAction = self.startToolBar.addAction("")
        self.__saveProjectAsAction = self.startToolBar.addAction("")
        self.__closeProjectAction = self.startToolBar.addAction("")

        self.__newProjectAction.triggered.connect(self.__newProject)
        self.__openProjectAction.triggered.connect(self.__openProject)
        self.__saveProjectAsAction.triggered.connect(self.__saveProjectAs)
        self.__closeProjectAction.triggered.connect(self.__closeProject)

        self.__recentProjectsMenu = QMenu("")
        self.startToolBar.insertAction(
            self.__saveProjectAsAction,
            self.__recentProjectsMenu.menuAction()
        )

    def __createEditToolBarActions(self):
        self.__undoAction = self.editToolBar.addAction("")
        self.__redoAction = self.editToolBar.addAction("")
        self.__undoRedoSeparator = self.editToolBar.addSeparator()
        self.__cutAction = self.editToolBar.addAction("")
        self.__copyAction = self.editToolBar.addAction("")
        self.__pasteAction = self.editToolBar.addAction("")
        self.__cutCopyPasteSeparator = self.editToolBar.addSeparator()
        self.__autoformatToolbarAction = self.editToolBar.addAction("")
        self.__sortImportsToolbarAction = self.editToolBar.addAction("")

        self.__autoformatToolbarAction.triggered.connect(
            self.__autoformatFirstEditor)
        self.__sortImportsToolbarAction.triggered.connect(
            self.__sortImportsInFirstEditor)
        self.__connectEditorActions(self.__editors[0])

    def __createAppsToolBarActions(self):
        self.appsToolBar.clear()
        for d in os.walk(os.path.join(
                os.path.dirname(__file__), "../apps/")):
            if "app.py" in d[2]:
                try:
                    spec = importlib.util.spec_from_file_location(
                        "app", os.path.join(d[0], "app.py"))
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    extClass = getattr(mod, mod.app)
                    a = self.appsToolBar.addAction(mod.name)
                    if self.__activeModule is None:
                        a.setEnabled(False)
                    if hasattr(mod, "icon"):
                        a.setIcon(QIcon(os.path.join(d[0], mod.icon)))
                    a.triggered.connect(lambda: self.__showAppGUI(extClass))
                except Exception as e:
                    print(e)

    def __createLibToolBarActions(self):
        self.libToolBar.clear()
        self.__pipGUIToolbarAction = self.libToolBar.addAction(
            translate("MainWindow", "pip package manager"))
        self.__pipGUIToolbarAction.setIcon(QIcon(os.path.join(
            os.path.dirname(__file__), "../icons/pipManager.png")))
        self.__pipGUIToolbarAction.triggered.connect(
            self.__openPipGUI)
        self.__addLibToolbarAction = self.libToolBar.addAction(
            translate("MainWindow", "Add lib path"))
        self.__libSeparator = self.libToolBar.addSeparator()
        self.__addLibToolbarAction.triggered.connect(self.__addLib)

        for path in self.__manager.config["libs"]:
            menu = QMenu(path, self.libToolBar)
            openAction = menu.addAction(translate("MainWindow", "Open folder"))
            openAction.triggered.connect(lambda: self.__open_file(path))
            deleteAction = menu.addAction(translate("MainWindow", "Delete"))
            deleteAction.triggered.connect(lambda: self.__deleteLib(path))
            self.libToolBar.addAction(menu.menuAction())

            if path not in sys.path:
                sys.path.append(path)

    def __createStreamToolBarActions(self):
        self.__dataToolbarAction = self.streamToolBar.addAction("")
        self.__plotToolbarAction = self.streamToolBar.addAction("")
        self.streamToolBar.addSeparator()
        self.__cleanToolbarAction = self.streamToolBar.addAction("")

        self.__dataToolbarAction.triggered.connect(self.__showStreamDataView)
        self.__plotToolbarAction.triggered.connect(self.__showStreamPlotView)
        self.__cleanToolbarAction.triggered.connect(self.__clearStream)

    def __createGitToolBarActions(self):
        self.__fetchToolbarAction = self.gitToolBar.addAction("")
        self.__pullToolbarAction = self.gitToolBar.addAction("")
        self.__pushToolbarAction = self.gitToolBar.addAction("")

        self.__fetchToolbarAction.triggered.connect(self.__gitTab.fetch)
        self.__pullToolbarAction.triggered.connect(self.__gitTab.pull)
        self.__pushToolbarAction.triggered.connect(self.__gitTab.push)

    def __createHelpToolBarActions(self):
        self.__preferencesToolbarAction = self.helpToolBar.addAction("")
        self.__userGuideToolbarAction = self.helpToolBar.addAction("")
        self.__aboutToolbarAction = self.helpToolBar.addAction("")
        self.__websiteToolbarAction = self.helpToolBar.addAction("")
        self.__debugToolbarAction = self.helpToolBar.addAction("")
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.helpToolBar.addWidget(spacer)

        self.__preferencesToolbarAction.triggered.connect(
            self.__showPreferences)
        self.__userGuideToolbarAction.triggered.connect(self.__showUserGuide)
        self.__aboutToolbarAction.triggered.connect(self.__showAboutWindow)
        self.__websiteToolbarAction.triggered.connect(self.__showPSWebsite)
        self.__debugToolbarAction.triggered.connect(
            self.__exportDebugInformation)

    def __getTemplateActions(self):
        templateDir = os.path.join(
            user_config_dir("Puzzlestream"), "templates")
        if not os.path.isdir(templateDir):
            os.makedirs(templateDir)
        shutil.copyfile(
            os.path.join(os.path.abspath(os.path.dirname(__file__)),
                         "../misc/templateReadme.md"),
            os.path.join(templateDir, "Readme.md")
        )
        actions = []
        for f in sorted(os.listdir(templateDir)):
            if (os.path.isfile(os.path.join(templateDir, f)) and
                    f.endswith(".py")):
                yield f[:-3]

    def __toggleFullscreen(self):
        if self.isFullScreen():
            if self.__lastWindowState == "maximized":
                self.showNormal()
                self.setWindowState(Qt.WindowMaximized)
            else:
                self.showNormal()
        else:
            if self.isMaximized():
                self.__lastWindowState = "maximized"
            else:
                self.__lastWindowState = "normal"
            self.showFullScreen()

    def __showPreferences(self):
        preferences = PSPreferencesWindow(self.__manager.config, self)
        preferences.show()

    def __showStreamDataView(self):
        view = PSDataView(self.__manager)
        currentDir = os.path.dirname(__file__)
        view.setStyleSheet(
            colors.parseQSS(currentDir + "/style/sheet-em.qss"))
        self.__manager.scene.statusChanged.connect(view.statusUpdate)
        view.closedSignal.connect(self.__removeFromWindowList)
        view.showMaximized()
        self.__subWindows.append(view)

    def __showStreamPlotView(self):
        view = PSPlotView(self.__manager, None)
        currentDir = os.path.dirname(__file__)
        view.setStyleSheet(
            colors.parseQSS(currentDir + "/style/sheet-em.qss"))
        self.__manager.scene.statusChanged.connect(view.statusUpdate)
        view.closedSignal.connect(self.__removeFromWindowList)
        view.show()
        self.__subWindows.append(view)

    def __showAppGUI(self, AppClass):
        if self.__activeModule is not None:
            app = AppClass(self.__activeModule.streamSection.data)
            app.showGUI(self.__activeModule.id, self.__manager.scene.modules,
                        self.__manager.stream, parent=self)
        else:
            notificationsystem.newNotification(
                translate(
                    "MainWindow",
                    "You have to choose a module before starting an app."
                )
            )

    def __removeFromWindowList(self, window: QMainWindow):
        i = self.__subWindows.index(window)
        self.__deleteTimer = QTimer()
        self.__deleteTimer.singleShot(
            20, lambda: self.__removeFromWindowListTimed(i))

    def __removeFromWindowListTimed(self, index: int):
        del self.__subWindows[index]
        gc.collect()

    def __clearStream(self):
        reply = QMessageBox.question(
            self,
            translate("MainWindow", "Confirm clean up"),
            translate(
                "MainWindow",
                "Are you sure you want to erase ALL data from the stream?"
            ),
            QMessageBox.No, QMessageBox.Yes
        )

        if reply == QMessageBox.Yes:
            self.__manager.stream.clear()

    def __showUserGuide(self):
        webbrowser.open_new_tab(
            "http://documentation.puzzlestream.org/index-user.html")

    def __showAboutWindow(self):
        about = PSAboutWindow(self)

    def __showPSWebsite(self):
        webbrowser.open_new_tab("https://puzzlestream.org")

    def __exportDebugInformation(self):
        path = QFileDialog.getSaveFileName(
            self,
            translate("MainWindow", "Save debug information"),
            filter=translate("MainWindow", "Zip files (*.zip)"),
            initialFilter="Debug.zip"
        )[0]

        if path != "":
            sys.stdout.flush()
            sys.stderr.flush()

            try:
                with zipfile.ZipFile(path, mode="w") as f:
                    configDir = user_config_dir("Puzzlestream")
                    logDir = os.path.join(configDir, "logs")
                    paths = [os.path.join(logDir, p)
                             for p in os.listdir(logDir)]

                    for p in paths:
                        f.write(p, arcname=os.path.basename(p))

                    if self.__manager.projectPath is not None:
                        puzzlePath = os.path.join(
                            self.__manager.projectPath, "puzzle.json")
                        if os.path.isfile(puzzlePath):
                            f.write(puzzlePath, arcname="puzzle.json")

                    configPath = os.path.join(configDir, "config.json")
                    if os.path.isfile(configPath):
                        f.write(configPath, arcname="config.json")

                notificationsystem.newNotification(
                    translate(
                        "MainWindow",
                        "The debug information was successfully saved to"
                    ) + " " + path + "."
                )
            except Exception as e:
                notificationsystem.newNotification(
                    translate(
                        "MainWindow",
                        "An error occured while saving the debug information:"
                    ) + e
                )

    def __updateRecentProjects(self):
        self.__recentProjectsMenu.clear()

        for item in self.__manager.config["last projects"][::-1]:
            action = self.__recentProjectsMenu.addAction(item)
            action.triggered.connect(
                lambda x, item=item: self.__openProject(item))

    def __connectEditorActions(self, editor: PSCodeEdit):
        self.__undoAction.triggered.connect(editor.undo)
        self.__redoAction.triggered.connect(editor.redo)
        self.__copyAction.triggered.connect(editor.copy)
        self.__cutAction.triggered.connect(editor.cut)
        self.__pasteAction.triggered.connect(editor.paste)

    def __disconnectEditorActions(self):
        self.__undoAction.triggered.disconnect()
        self.__redoAction.triggered.disconnect()
        self.__copyAction.triggered.disconnect()
        self.__cutAction.triggered.disconnect()
        self.__pasteAction.triggered.disconnect()

    def __createPuzzleToolBarActions(self):
        self.__runAction = QAction(self)
        self.__pauseAction = QAction(self)
        self.__stopAction = QAction(self)
        self.__newModuleMenu = QMenu("", self)
        self.__newIntModuleAction = self.__newModuleMenu.addAction("")
        self.__newExtModuleAction = self.__newModuleMenu.addAction("")
        self.__newTemplateModuleMenu = self.__newModuleMenu.addMenu("")
        self.__newPipeAction = QAction("", self)
        self.__newValveAction = QAction("", self)

        self.__newTemplateModuleMenu.aboutToShow.connect(
            self.__createTemplateModuleMenuActions)

        self.__runAction.triggered.connect(self.__run)
        self.__pauseAction.triggered.connect(self.__pause)
        self.__stopAction.triggered.connect(self.__stop)
        self.__newModuleMenu.menuAction().triggered.connect(
            self.__newIntModule)
        self.__newIntModuleAction.triggered.connect(self.__newIntModule)
        self.__newExtModuleAction.triggered.connect(self.__newExtModule)
        self.__newPipeAction.triggered.connect(self.__newPipe)
        self.__newValveAction.triggered.connect(self.__newValve)

    def __createTemplateModuleMenuActions(self):
        self.__newTemplateModuleMenu.clear()
        for a in self.__getTemplateActions():
            action = self.__newTemplateModuleMenu.addAction(a)
            action.triggered.connect(
                lambda _, p=a: self.__newIntModuleFromTemplate(templatePath=p))
        action = self.__newTemplateModuleMenu.addAction(
            translate("MainWindow", "-> Manage templates"))
        path = os.path.join(user_config_dir("Puzzlestream"), "templates")
        action.triggered.connect(lambda _, p=path: self.__open_file(p))

    def __getPuzzleToolBarActions(self):
        return [self.__runAction, self.__pauseAction, self.__stopAction,
                self.__newModuleMenu.menuAction(), self.__newPipeAction,
                self.__newValveAction]

    def updateText(self, module: PSModule, text: str):
        if module == self.__activeModule:
            if text is None:
                self.outputTextEdit.setText("")
                self.outputTextEdit.activateAutoscroll()
            else:
                cursor = self.outputTextEdit.textCursor()
                cursor.movePosition(cursor.End)
                f = cursor.charFormat()
                f.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
                cursor.insertText(text, f)

    def updateStatus(self, module: PSModule):
        if module == self.__activeModule:
            self.statisticsTextEdit.setHtml(module.statistics)
            self.updateActiveModuleButtons()

    def updateActiveModuleButtons(self):
        currentDir = os.path.dirname(__file__)

        if self.__currentStyle == "dark":
            if (self.__activeModule is not None and
                    self.__activeModule.status is PSStatus.RUNNING):
                self.btnRunPauseActive.setIcon(QIcon(os.path.join(
                    currentDir, "../icons/pause_blue_in.png")))
            else:
                self.btnRunPauseActive.setIcon(QIcon(os.path.join(
                    currentDir, "../icons/play_blue_in.png")))
        elif (self.__activeModule is not None and
                self.__currentStyle == "light"):
            if self.__activeModule.status is PSStatus.RUNNING:
                self.btnRunPauseActive.setIcon(QIcon(os.path.join(
                    currentDir, "../icons/pause_blue_out.png")))
            else:
                self.btnRunPauseActive.setIcon(QIcon(os.path.join(
                    currentDir, "../icons/play_blue_out.png")))

        if self.__activeModule is not None:
            self.__editorWidgets[0].editorFilePathLabel.setText(
                self.__activeModule.filePath + " - " +
                translate("Status", str(self.__activeModule.status))
            )

    def __updateGitTabHeaderAndMenu(self):
        self.__manager.save()
        self.outputTabWidget.setTabText(
            2, "Git - %s (%d)" % (self.__gitTab.activeBranchName,
                                  self.__gitTab.numberOfChangedItems))

        for a in [self.__pullToolbarAction, self.__pushToolbarAction]:
            a.setEnabled(self.__gitTab.hasRemote)

    def __configChanged(self, key: str):
        if key == "last projects":
            self.__updateRecentProjects()
        elif key == "saveOnEditorFocusOut":
            for e in self.__editors:
                e.save_on_focus_out = self.__manager.config[
                    "saveOnEditorFocusOut"]
        elif key == "design":
            design = self.__manager.config["design"]
            self.__setStyle(design[1][design[0]])

    def __updateNotificationHeader(self, added=False):
        self.outputTabWidget.setTabText(
            3,
            translate("MainWindow", "Notifications") + " (%d)" % (
                len(self.__notificationTab.notifications))
        )
        if added:
            self.outputTabWidget.setCurrentIndex(3)

    """
        reaction routines
    """

    def __deactivate(self):
        for e in self.__editorWidgets:
            e.hide()
        self.__welcomeLabel.setText(self.__newProjectText)
        self.__welcomeLabel.show()
        self.__resetActiveModule()
        for e in self.__activeElements:
            e.setEnabled(False)

    def __activate(self):
        self.__welcomeLabel.setText(self.__projectOpenText)
        for e in self.__activeElements:
            e.setEnabled(True)

    def __updateProjectLoadedStatus(self):
        if self.__manager.projectPath is None:
            self.__deactivate()
        else:
            self.__activate()
            self.mainTabWidget.setCurrentIndex(2)

    def __welcomeLabelLinkActivated(self, link: str):
        if link == "#new_project":
            self.__newProject()
        elif link == "#open_project":
            self.__openProject()
        elif link.startswith("#last_project:"):
            link = link.replace("#last_project:", "")
            self.__openProject(link)

    def __newProject(self, path: str = None):
        if not isinstance(path, str):
            path = QFileDialog.getExistingDirectory(
                self,
                translate("MainWindow", "New project folder")
            )

        if path != "":
            if len(os.listdir(path)) == 0:
                self.__manager.newProject(path)
                self.setWindowTitle(
                    "Puzzlestream - " + self.__manager.projectPath)
                self.__resetUI(path)
            else:
                msg = QMessageBox(self)
                msg.setText(translate("MainWindow", "Directory not empty."))
                msg.show()

        self.__updateProjectLoadedStatus()
        self.__gitTab.setRepo(self.__manager.repo)

    def __openProject(self, path: str = None, start: bool = False):
        if (path is None or not isinstance(path, str)) and not start:
            path = QFileDialog.getExistingDirectory(
                self,
                translate("MainWindow", "Open project folder")
            )

        if os.path.isdir(path):
            self.__deactivate()
            self.__closeProject()
            self.__welcomeLabel.setText(
                translate("MainWindow", "Loading project...") + "<br>" + path)
            QApplication.processEvents()
            if os.path.isfile(path + "/puzzle.json"):
                self.__manager.load(path, silent=start)
                self.setWindowTitle("Puzzlestream - " + path)
                self.__resetUI(path)
                for e in self.__editorWidgets:
                    e.fileExplorer.setPath(path)
            elif not start:
                msg = QMessageBox(self)
                msg.setText(
                    translate(
                        "MainWindow",
                        "The chosen project folder is not valid. " +
                        "Please choose another one.")
                )
                msg.exec()
                self.__openProject()

        self.__updateProjectLoadedStatus()
        self.__gitTab.setRepo(self.__manager.repo)
        if self.__btnPuzzleLock.isChecked() != self.__manager.puzzleLocked:
            self.__btnPuzzleLock.click()
        self.__togglePuzzleLocked()

    def __closeProject(self):
        if self.__manager.projectPath is not None:
            self.__manager.closeProject()
        self.__deactivate()
        self.__gitTab.setRepo(None)
        self.changeRightWidgetMode("puzzle")

    def __saveProjectAs(self, path: str = None):
        if not isinstance(path, str):
            path = QFileDialog.getExistingDirectory(
                self,
                translate("MainWindow", "Save project folder")
            )

        if os.path.isdir(path):
            if len(os.listdir(path)) == 0:
                self.__manager.saveAs(path)
                self.setWindowTitle("Puzzlestream - " + path)
                self.__resetUI(path)
            else:
                msg = QMessageBox(self)
                msg.setText(translate("MainWindow", "Directory not empty."))
                msg.show()

        self.__updateProjectLoadedStatus()

    def __saveFileToolbar(self, value: bool):
        self.__saveOpenFiles()

    def __abortAdding(self):
        self.__manager.addStatus = None
        self.__btnAddStatusAction.setVisible(False)
        self.__enableAddActions()
        self.__puzzleLabel.setText("")
        self.__welcomeLabel.setText(self.__projectOpenText)

    def __newIntModule(self):
        self.__disableAddActions()
        self.__welcomeLabel.setText(self.__newItemText + "module.")
        self.__manager.addStatus = "intModule"
        self.__puzzleLabel.setText(
            translate(
                "MainWindow",
                "Click on a free spot inside the puzzle view to add a new " +
                "internal module."
            )
        )
        self.__btnAddStatusAction.setVisible(True)

    def __newExtModule(self):
        self.__disableAddActions()
        self.__welcomeLabel.setText(self.__newItemText + "module.")
        self.__manager.addStatus = "extModule"
        self.__puzzleLabel.setText(
            translate(
                "MainWindow",
                "Click on a free spot inside the puzzle view to add a new " +
                "external module."
            )
        )
        self.__btnAddStatusAction.setVisible(True)

    def __newIntModuleFromTemplate(self, templatePath: str):
        self.__disableAddActions()
        self.__welcomeLabel.setText(self.__newItemText + "module.")
        self.__manager.addStatus = "template " + templatePath
        self.__puzzleLabel.setText(
            translate(
                "MainWindow",
                "Click on a free spot inside the puzzle view to add a new " +
                "internal module from the \"%s\" template." % (templatePath)
            )
        )
        self.__btnAddStatusAction.setVisible(True)

    def __newPipe(self):
        self.__disableAddActions()
        self.__welcomeLabel.setText(self.__newItemText + "pipe.")
        self.__manager.addStatus = "pipe"
        self.__puzzleLabel.setText(
            translate(
                "MainWindow",
                "Click on a free spot inside the puzzle view to add a new " +
                "pipe."
            )
        )
        self.__btnAddStatusAction.setVisible(True)

    def __newValve(self):
        self.__disableAddActions()
        self.__welcomeLabel.setText(self.__newItemText + "valve.")
        self.__manager.addStatus = "valve"
        self.__puzzleLabel.setText(
            translate(
                "MainWindow",
                "Click on a free spot inside the puzzle view to add a new " +
                "valve."
            )
        )
        self.__btnAddStatusAction.setVisible(True)

    def __resetActiveModule(self):
        self.__activeModule = None
        for a in self.appsToolBar.actions():
            a.setEnabled(False)
        for a in [self.__plotViewAction, self.__dataViewAction]:
            a.setEnabled(False)

    def __itemAdded(self, item: PSPuzzleItem):
        self.__enableAddActions()
        self.__welcomeLabel.setText(self.__projectOpenText)
        self.__puzzleLabel.setText("")
        self.__btnAddStatusAction.setVisible(False)

        if self.__manager.puzzleLocked:
            self.__btnPuzzleLock.click()
            self.__togglePuzzleLocked()

        self.__manager.save()
        self.__gitTab.reload()

    def __itemDeleted(self, item: PSPuzzleItem):
        if item == self.__activeModule:
            self.__welcomeLabel.setText(self.__projectOpenText)
            self.__editorWidgets[0].hide()
            self.__welcomeLabel.show()
            self.horizontalSplitter.setStretchFactor(0, 0)
            self.__resetActiveModule()

        self.__manager.save()
        self.__gitTab.reload()

    def __togglePuzzleLocked(self, *args):
        if self.__btnPuzzleLock.isChecked():
            self.__manager.setAllItemsFixed()
            self.__lblPuzzleLock.setText(
                translate("MainWindow", "puzzle locked"))
        else:
            self.__manager.setAllItemsMovable()
            self.__lblPuzzleLock.setText(
                translate("MainWindow", "puzzle unlocked"))

        self.__manager.save()
        self.__gitTab.reload()

    def __enableAddActions(self):
        for a in self.puzzleToolBar.actions():
            if not isinstance(a, QWidgetAction):
                a.setEnabled(True)
        self.__btnPuzzleLock.setEnabled(True)

        for a in (self.__runAction, self.__pauseAction, self.__stopAction):
            a.setEnabled(True)

    def __disableAddActions(self):
        for a in self.puzzleToolBar.actions():
            if not isinstance(a, QWidgetAction):
                a.setEnabled(False)
        self.__btnPuzzleLock.setEnabled(False)

        for a in (self.__runAction, self.__pauseAction, self.__stopAction):
            a.setEnabled(False)

    def __showData(self, puzzleItem: PSPuzzleItem):
        view = PSDataView(self.__manager, puzzleItem)
        currentDir = os.path.dirname(__file__)
        view.setStyleSheet(
            colors.parseQSS(currentDir + "/style/sheet-em.qss"))
        self.__manager.scene.statusChanged.connect(view.statusUpdate)
        view.closedSignal.connect(self.__removeFromWindowList)
        view.showMaximized()
        self.__subWindows.append(view)

    def __showPlots(self, puzzleItem: PSPuzzleItem):
        view = PSPlotView(self.__manager, puzzleItem)
        currentDir = os.path.dirname(__file__)
        view.setStyleSheet(
            colors.parseQSS(currentDir + "/style/sheet-em.qss"))
        self.__manager.scene.statusChanged.connect(view.statusUpdate)
        view.closedSignal.connect(self.__removeFromWindowList)
        view.show()
        self.__subWindows.append(view)

    def __run(self):
        if (self.__activeModule is not None and
                self.__manager.config["saveOnRun"]):
            self.__saveOpenFiles()

        for module in self.__manager.scene.modules.values():
            if ((module.status is PSStatus.INCOMPLETE or
                 module.status is PSStatus.FINISHED or
                 module.status is PSStatus.ERROR or
                 module.status is PSStatus.TESTFAILED) and
                    not module.hasInput):
                module.run()
            else:
                module.resume()

    def __pause(self):
        for module in self.__manager.scene.modules.values():
            module.pause()

    def __stop(self):
        for module in self.__manager.scene.modules.values():
            module.stop()

    """
    ===========================================================================
        Pip stuff
    """

    def __openPipGUI(self):
        window = PSPipGUI(parent=self)
        window.show()

    """
    ===========================================================================
        Lib stuff
    """

    def __addLib(self):
        path = QFileDialog.getExistingDirectory(
            self,
            translate("MainWindow", "Add lib folder")
        )
        if os.path.isdir(path):
            self.__manager.addLib(path)

            args = ["-s" + lib for lib in self.__manager.config["libs"]]

            for e in self.__editors:
                e.backend.start(
                    server.__file__, args=args)
            self.__createLibToolBarActions()

    def __open_file(self, filename: str):
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])

    def __deleteLib(self, path: str):
        self.__manager.deleteLib(path)
        self.__createLibToolBarActions()

        if path in sys.path:
            i = sys.path.index(path)
            del sys.path[i]

    """
    ===========================================================================
        Update check stuff
    """

    def __checkForUpdates(self):
        self.__updateStatus = None

        try:
            version = pkg_resources.get_distribution("puzzlestream").version
            with urlopen("https://pypi.org/pypi/puzzlestream/json") as res:
                versionAvailable = json.loads(res.read())["info"]["version"]
                self.__updateStatus = (version, versionAvailable)
        except Exception as e:
            print(e)

    def __updateCheckFinished(self):
        if isinstance(self.__updateStatus, tuple):
            linkEnding = translate("MainWindow", "get-puzzlestream/")

            if sys.platform == "linux" or sys.platform == "linux2":
                linkEnding += "linux"
            elif sys.platform == "darwin":
                linkEnding += "mac-os-x"
            elif sys.platform == "win32" or sys.platform == "win64":
                linkEnding += "windows"

            version, versionAvailable = self.__updateStatus
            if LooseVersion(versionAvailable) > LooseVersion(version):
                notificationsystem.newNotification(
                    translate("MainWindow", "An update to version ") +
                    str(versionAvailable) +
                    translate(
                        "MainWindow",
                        " is available; you are " +
                        "currently using version "
                    ) + str(version) + ". " +
                    translate(
                        "MainWindow",
                        "Please click <a href=\"https://puzzlestream.org/"
                    ) + linkEnding +
                    translate(
                        "MainWindow",
                        "\">here</a> for update instructions."
                    )
                )
