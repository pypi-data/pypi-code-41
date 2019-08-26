# -*- coding: utf-8 -*-
"""Data view module.

contains PSDataView
"""

import gc

import matplotlib.backends.backend_qt5agg as mplAgg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyqtgraph as pg
from matplotlib.figure import Figure
from puzzlestream.backend.numpymodel2D import PSNumpyModel2D
from puzzlestream.backend.reference import PSCacheReference
from puzzlestream.backend.signal import PSSignal
from puzzlestream.backend.standardtablemodel import PSStandardTableModel
from puzzlestream.backend.status import PSStatus
from puzzlestream.backend.stream import PSStream
from puzzlestream.backend.treemodel import PSTreeModel
from puzzlestream.ui.dataviewexport import PSTableExportDialog
from puzzlestream.ui.manager import PSManager
from puzzlestream.ui.plot import KeyPlot, Plot
from puzzlestream.ui.puzzleitem import PSPuzzleItem
from puzzlestream.ui.tracebackview import PSTracebackView
from PyQt5 import QtCore, QtGui, QtWidgets

translate = QtCore.QCoreApplication.translate


class PSDataView(QtWidgets.QMainWindow):
    """Data view with table, plots and export functionality.

    One of the central parts of Puzzlestream; the data view shows
    1D and 2D numpy arrays, matplotlib plots, ...
    Everything that cannot be dealt with is simply shown as its string
    representation.
    """

    def __init__(self, manager: PSManager, puzzleItem: PSPuzzleItem = None,
                 parent: QtCore.QObject = None):
        """Data view init.

        Args:
            manager (PSManager): Current Puzzlestream manager instance.
            puzzleItem (PSPuzzleItem): Puzzle item whose data is to be
                displayed.
            parent: Qt parent widget.
        """
        super().__init__(parent)

        self.__stream = manager.stream

        if puzzleItem is None:
            self.__data = self.__stream
        else:
            self.__data = puzzleItem.streamSection.data

        self.__puzzleItem = puzzleItem
        self.__modules = manager.scene.modules
        self.__config = manager.config
        self.__mplPlotWidget = None
        self.__lastPlotSize = None
        self.__x, self.__y = None, None
        self.__keys, self.__retranslatedKeys = None, None

        # horizontal splitter
        self.horizontalSplitter = QtWidgets.QSplitter()
        self.horizontalSplitter.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSplitter.setContentsMargins(0, 0, 0, 0)
        self.horizontalSplitter.setObjectName("horizontalSplitter")
        self.setCentralWidget(self.horizontalSplitter)

        # table view - added to the horizontal splitter
        self.tableView = QtWidgets.QTableView(self.horizontalSplitter)
        self.tableView.setEditTriggers(QtWidgets.QTableView.NoEditTriggers)
        self.tableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(
            self.tableContextMenu)
        self.tableView.horizontalHeader().setDefaultSectionSize(132)
        self.tableView.setWordWrap(False)
        self.horizontalSplitter.addWidget(self.tableView)

        # text edit for showing other items
        self.textEdit = QtWidgets.QTextEdit()
        self.textEdit.setReadOnly(True)
        self.textEdit.setFont(
            QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont))
        self.textEdit.hide()

        # vertical layout on the right side
        self.verticalSplitter = QtWidgets.QSplitter(self.horizontalSplitter)
        self.verticalSplitter.setOrientation(QtCore.Qt.Vertical)
        self.verticalSplitter.setContentsMargins(0, 0, 5, 0)
        self.horizontalSplitter.addWidget(self.verticalSplitter)

        self.horizontalSplitter.setStretchFactor(2, 2)

        # tree model and view
        self.treeView = QtWidgets.QTreeView(self.verticalSplitter)
        self.treeView.setEditTriggers(QtWidgets.QTreeView.NoEditTriggers)
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(
            self.treeContextMenu)
        self.treeView.header().close()

        # pyqtgraph plot widget
        self.plotGroupWidget = QtWidgets.QWidget(self.verticalSplitter)
        self.plotGroupWidgetLayout = QtWidgets.QVBoxLayout(
            self.plotGroupWidget)
        self.plotGroupWidgetLayout.setContentsMargins(0, 0, 0, 0)
        self.plotWidget = pg.PlotWidget(self.plotGroupWidget)
        self.plotCurve = pg.PlotCurveItem()
        self.plotWidget.addItem(self.plotCurve)

        # drop downs and swap button
        self.dropdownX = QtWidgets.QComboBox(self.plotGroupWidget)
        self.dropdownY = QtWidgets.QComboBox(self.plotGroupWidget)
        self.dropdownX.currentIndexChanged.connect(self.__setXDropdown)
        self.dropdownY.currentIndexChanged.connect(self.__setYDropdown)
        self.swapBtn = QtWidgets.QPushButton(self.plotGroupWidget)
        self.swapBtn.setStyleSheet(
            "QPushButton { min-width: 7em; max-width: 7em; }")
        self.swapBtn.clicked.connect(self.__swapAxes)
        self.hboxDropdown = QtWidgets.QHBoxLayout()
        self.hboxDropdown.addWidget(self.dropdownX)
        self.hboxDropdown.addWidget(self.swapBtn)
        self.hboxDropdown.addWidget(self.dropdownY)

        # add hbox and plot widget to plotGroupWidgetLayout
        self.plotGroupWidgetLayout.addLayout(self.hboxDropdown)
        self.plotGroupWidgetLayout.addWidget(self.plotWidget)

        # create matplotlib group widget
        self.mplGroupWidget = QtWidgets.QWidget(self.verticalSplitter)
        self.mplLayout = QtWidgets.QVBoxLayout(self.mplGroupWidget)
        self.mplGroupWidget.setLayout(self.mplLayout)

        # add tree view and group widgets to vertical layout, hide mpl widget
        self.verticalSplitter.addWidget(self.treeView)
        self.verticalSplitter.addWidget(self.plotGroupWidget)
        self.verticalSplitter.addWidget(self.mplGroupWidget)
        self.verticalSplitter.setCollapsible(1, True)
        self.verticalSplitter.setCollapsible(2, True)
        self.hideMplWidget()

        # resize horizontal splitter
        self.horizontalSplitter.setStretchFactor(0, 6)
        self.horizontalSplitter.setStretchFactor(1, 4)

        # create main menu
        self.toolbar = QtWidgets.QToolBar(self)
        self.toolbar.setMovable(False)
        self.completeExportAction = self.toolbar.addAction("")
        self.completeExportAction.triggered.connect(self.exportCompleteTable)
        self.addToolBar(self.toolbar)

        # create status bar
        self.setStatusBar(QtWidgets.QStatusBar())
        self.statusBarLabel = QtWidgets.QLabel()
        self.statusBar().addWidget(self.statusBarLabel)

        # finalise setup
        self.__checkStates = {}
        self.__currentModelType = "none"
        self.__closedSignal = PSSignal()
        self.retranslateUi()
        self.update()

    @property
    def closedSignal(self) -> PSSignal:
        return self.__closedSignal

    def retranslateUi(self):
        if self.__puzzleItem is None:
            self.setWindowTitle(
                translate("DataView", "Data view") + " - " +
                translate("DataView", "complete stream")
            )
        else:
            self.setWindowTitle(
                translate("DataView", "Data view") + " - " +
                str(self.__puzzleItem)
            )

        self.completeExportAction.setText(
            translate("DataView", "Export complete table"))
        self.swapBtn.setText(translate("DataView", "swap axes"))

        if self.treeView.model() is not None:
            self.treeView.model().retranslateUi()

    def changeEvent(self, event: QtCore.QEvent):
        if event.type() == QtCore.QEvent.LanguageChange:
            self.retranslateUi()
        return super().changeEvent(event)

    def statusUpdate(self, item: PSPuzzleItem):
        if item.status is PSStatus.FINISHED:
            if self.__puzzleItem is None or item == self.__puzzleItem:
                if not isinstance(self.__data, PSStream):
                    self.__data.reload()
                self.update(item)

    def update(self, sourceItem: PSPuzzleItem = None):
        if self.__puzzleItem is not None or sourceItem is None:
            needsUpdate = True
        else:
            needsUpdate = False
            if self.__puzzleItem is not None:
                for key in self.__data:
                    if (int(key.split("-")[0]) == sourceItem.id and not
                            isinstance(
                                self.__data.__getitem__(key, traceback=False),
                                PSCacheReference
                    )):
                        needsUpdate = True
                        break
            else:
                for key in self.__data:
                    if (int(key.split("-")[0]) == sourceItem.id and not
                            isinstance(
                                self.__data.__getitem__(key),
                                PSCacheReference
                    )):
                        needsUpdate = True
                        break

        if needsUpdate:
            s = self.verticalSplitter.sizes()
            if len(self.treeView.selectedIndexes()) > 0:
                i = self.treeView.selectedIndexes()[0]
                restoreKey = self.treeView.model().data(i, 0)
            else:
                restoreKey = None

            if not isinstance(self.__data, PSStream):
                self.__data.cleanRam()
            self.hideMplWidget()
            self.createClassificationLists()
            self.createTree()
            self.createDropdowns()

            if (isinstance(self.tableView.model(), PSStandardTableModel) or
                    self.tableView.model() is None):
                self.setToStandardModel(forceUpdate=True)
            if restoreKey is not None and restoreKey in self.__keys:
                self.selectKey(restoreKey)

            if sum(s) > 0:
                self.verticalSplitter.setSizes([s[0], sum(s) - s[0]])
            else:
                self.verticalSplitter.setSizes([1, 1])

    def updatePuzzleItem(self, puzzleItem: PSPuzzleItem):
        self.__puzzleItem = puzzleItem
        self.__data = puzzleItem.streamSection.data
        if puzzleItem.status is PSStatus.FINISHED:
            self.update()

    def createClassificationLists(self):
        self.__keys = []
        for key in sorted(self.__data):
            try:
                if (self.__puzzleItem is not None or
                        key not in self.__data.references):
                    self.__keys.append(key)
            except Exception as e:
                print(e)

        self.__standardKeys, self.__numpy2DKeys, self.__mplKeys = [], [], []
        self.__pandasDataFrameKeys, self.__otherKeys = [], []

        for key in self.__keys:
            try:
                data = self.__data[key]
                tKey = self.__translateKeyToUser(key)

                if tKey is not None:
                    if isinstance(data, np.ndarray) or isinstance(data, pd.Series):
                        if len(data.shape) == 1:
                            self.__standardKeys.append(tKey)
                        elif len(data.shape) == 2:
                            self.__numpy2DKeys.append(tKey)
                    elif isinstance(data, pd.DataFrame):
                        self.__pandasDataFrameKeys.append(tKey)
                    elif isinstance(data, Figure):
                        self.__mplKeys.append(tKey)
                    else:
                        self.__otherKeys.append(tKey)
            except Exception as e:
                print(e)

    def createDropdowns(self):
        indDropdownX = self.dropdownX.currentIndex()
        indDropdownY = self.dropdownY.currentIndex()
        self.dropdownX.setCurrentIndex(0)
        self.dropdownY.setCurrentIndex(0)
        self.dropdownX.clear()
        self.dropdownY.clear()
        self.dropdownX.addItem("empty")

        if isinstance(self.tableView.model(), PSStandardTableModel):
            for i, key in enumerate(self.tableView.model().keys):
                try:
                    if (self.tableView.model().modelData[i].dtype in
                        [int, float, np.int32, np.int64, np.float32,
                         np.float64, "int32", "int64", "float32", "float64"]):
                        self.dropdownX.addItem(key)
                        self.dropdownY.addItem(key)
                except Exception as e:
                    print(e)

        if indDropdownX > 0 and indDropdownX < self.dropdownX.count():
            self.dropdownX.setCurrentIndex(indDropdownX)
        if indDropdownY > 0 and indDropdownY < self.dropdownY.count():
            self.dropdownY.setCurrentIndex(indDropdownY)

    def __translateKeyToUser(self, key: str) -> str:
        if isinstance(self.__data, PSStream):
            ID = key.split("-")[0]
            if not int(ID) in self.__modules:
                return
            keyn = key[len(ID) + 1:]
            return self.__modules[int(ID)].name + ": " + keyn
        return key

    def __translateKeyToInternal(self, key: str) -> str:
        if key in self.__retranslatedKeys:
            return self.__retranslatedKeys[key]

    def createTree(self):
        model = PSTreeModel(self.__standardKeys, self.__numpy2DKeys,
                            self.__pandasDataFrameKeys, self.__mplKeys,
                            self.__otherKeys, self.__checkStates)
        self.__retranslatedKeys = {self.__translateKeyToUser(key): key
                                   for key in self.__keys}
        if None in self.__retranslatedKeys:
            del self.__retranslatedKeys[None]

        model.itemChanged.connect(self.__treeItemChanged)
        self.treeView.setModel(model)
        self.treeView.selectionModel().selectionChanged.connect(
            self.__treeSelectionChanged)
        self.treeView.expandAll()

    def setToStandardModel(self, selectColumn: str = None,
                           forceUpdate: bool = False):
        if not isinstance(self.__data, PSStream):
            self.__data.cleanRam()
        self.hideTextEdit()
        self.showTableViewHeaders()

        if forceUpdate or self.currentModelType != "standard":
            model = PSStandardTableModel()

            for key in self.__standardKeys:
                if self.__checkStates[key]:
                    model.addColumn(
                        key, self.__data[self.__translateKeyToInternal(key)])
            self.tableView.setModel(model)
            self.__currentModelType = "standard"
            self.tableView.selectionModel().selectionChanged.connect(
                self.__tableSelectionChanged)
            self.__recreateColumnPlots()
            self.createDropdowns()

            self.tableView.setRowHeight(0, 90)
        else:
            model = self.tableView.model()

        if isinstance(selectColumn, str) and selectColumn in model.keys:
            index = model.keys.index(selectColumn)
            self.tableView.selectColumn(index)
            self.treeView.setFocus()

    def __recreateColumnPlots(self):
        model = self.tableView.model()

        for i in range(len(model.keys)):
            w = model.getPlotWidget(i)

            if w is not None:
                self.tableView.setIndexWidget(model.index(0, i), w)

        gc.collect()

    def setToPandasDataFrameModel(self, key: str, selectColumn: str = None,
                                  forceUpdate: bool = False):
        if not isinstance(self.__data, PSStream):
            self.__data.cleanRam()
        self.hideTextEdit()
        self.showPlotWidget()

        self.showTableViewHeaders()

        if forceUpdate or self.currentModelType != "pandasdataframe":
            model = PSStandardTableModel()

            frame = self.__data[self.__translateKeyToInternal(key)]
            for key in frame:
                model.addColumn(key, frame[key])
            self.tableView.setModel(model)
            self.__currentModelType = "pandasdataframe"
            self.tableView.selectionModel().selectionChanged.connect(
                self.__tableSelectionChanged)
            self.__recreateColumnPlots()
            self.createDropdowns()

            self.tableView.setRowHeight(0, 80)
        else:
            model = self.tableView.model()

        if isinstance(selectColumn, str) and selectColumn in model.keys:
            index = model.keys.index(selectColumn)
            self.tableView.selectColumn(index)
            self.treeView.setFocus()

    def setToNumpy2DModel(self, key: str):
        if not isinstance(self.__data, PSStream):
            self.__data.cleanRam()
        self.hideTextEdit()

        self.showTableViewHeaders()

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        data = self.__data[self.__translateKeyToInternal(key)]

        model = PSNumpyModel2D(data)
        self.tableView.setModel(model)
        self.__currentModelType = "2D"
        self.tableView.selectionModel().selectionChanged.connect(
            self.__tableSelectionChanged)
        self.tableView.setRowHeight(0, 30)

        self.showMplWidget()

        fig = Figure()
        ax = fig.add_subplot(111)
        p = ax.imshow(data)
        fig.colorbar(p)
        fig.tight_layout()
        self.__mplPlotWidget = Plot(fig, self.mplGroupWidget)

        self.mplLayout.addWidget(self.__mplPlotWidget)
        QtWidgets.QApplication.restoreOverrideCursor()

    def setToOtherModel(self, key: str):
        if not isinstance(self.__data, PSStream):
            self.__data.cleanRam()
        self.hideMplWidget()
        self.hidePlotWidget()

        try:
            text = str(self.__data[self.__translateKeyToInternal(key)])
        except Exception as e:
            text = str(e)
        self.textEdit.setText(text)

        self.showTextEdit()
        self.__currentModelType = "none"

    def showTableViewHeaders(self):
        self.tableView.horizontalHeader().setStretchLastSection(False)
        self.tableView.verticalHeader().setStretchLastSection(False)
        self.tableView.horizontalHeader().show()
        self.tableView.verticalHeader().show()

    def hideTableViewHeaders(self):
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.verticalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().hide()
        self.tableView.verticalHeader().hide()

    def showTextEdit(self):
        if not self.textEdit.isVisible():
            sizes = self.horizontalSplitter.sizes()
            self.tableView.hide()
            self.textEdit.show()
            self.horizontalSplitter.insertWidget(0, self.textEdit)
            self.tableView.setParent(None)
            if sum(sizes) > 0:
                self.horizontalSplitter.setSizes(
                    [sum(sizes) - sizes[-1], sizes[-1]])

    def hideTextEdit(self):
        if not self.tableView.isVisible():
            sizes = self.horizontalSplitter.sizes()
            self.tableView.show()
            self.textEdit.hide()
            self.horizontalSplitter.insertWidget(0, self.tableView)
            self.textEdit.setParent(None)
            if sum(sizes) > 0:
                self.horizontalSplitter.setSizes(
                    [sum(sizes) - sizes[-1], sizes[-1]])

    @property
    def currentModelType(self) -> str:
        return self.__currentModelType

    """
    ===========================================================================
        Tree selection / item changed handlers and routines
    """

    def __treeItemChanged(self, item: QtWidgets.QTreeWidgetItem):
        self.hideMplWidget()

        userKey = item.text()
        key = self.__translateKeyToInternal(userKey)
        self.__checkStates[key] = item.checkState() == 2
        model = self.tableView.model()

        if isinstance(model, PSStandardTableModel):
            if self.__checkStates[key] and key not in model.keys:
                tKey = self.__translateKeyToUser(key)
                if tKey is not None:
                    self.tableView.model().addColumn(tKey, self.__data[key])
                    self.__recreateColumnPlots()
            elif not self.__checkStates[key] and userKey in model.keys:
                self.tableView.model().deleteColumn(userKey)
                self.__recreateColumnPlots()

            self.tableView.model().layoutChanged.emit()

        if not isinstance(self.__data, PSStream):
            self.__data.cleanRam()

    def __treeSelectionChanged(self):
        i = self.treeView.selectedIndexes()[0]
        key = self.treeView.model().data(i, 0)

        if key in self.__numpy2DKeys:
            self.numpy2DItemSelected(key)
        elif key in self.__pandasDataFrameKeys:
            self.pandasDataFrameSelected(key)
        elif key in self.__mplKeys:
            self.matplotlibItemSelected(key)
        elif key in self.__standardKeys:
            self.standardItemSelected(key)
        elif key in self.__otherKeys:
            self.otherItemSelected(key)

    def selectKey(self, key: str):
        if key in self.__standardKeys:
            i = self.__standardKeys.index(key)
            item = self.treeView.model().item(0, 0)
        if key in self.__numpy2DKeys:
            i = self.__numpy2DKeys.index(key)
            item = self.treeView.model().item(1, 0)
        elif key in self.__pandasDataFrameKeys:
            i = self.__pandasDataFrameKeys.index(key)
            item = self.treeView.model().item(2, 0)
        elif key in self.__mplKeys:
            i = self.__mplKeys.index(key)
            item = self.treeView.model().item(3, 0)
        elif key in self.__otherKeys:
            i = self.__otherKeys.index(key)
            item = self.treeView.model().item(4, 0)

        ind = item.child(i, 0).index()
        self.treeView.selectionModel().select(
            ind, QtCore.QItemSelectionModel.Select)

    def standardItemSelected(self, key: str):
        self.setToStandardModel(key)
        self.showPlotWidget()

    def numpy2DItemSelected(self, key: str):
        self.setToNumpy2DModel(key)

    def pandasDataFrameSelected(self, key: str):
        self.setToPandasDataFrameModel(key)

    def matplotlibItemSelected(self, key: str):
        i = self.treeView.selectedIndexes()[0]
        self.treeView.setCurrentIndex(i)
        self.showMplWidget()

        self.__mplPlotWidget = KeyPlot(self.__data,
                                       self.__translateKeyToInternal(key))
        self.mplLayout.addWidget(self.__mplPlotWidget)

    def otherItemSelected(self, key: str):
        self.setToOtherModel(key)

    def __deleteItem(self):
        i = self.treeView.selectedIndexes()[0]
        userKey = self.treeView.model().data(i, 0)
        key = self.__translateKeyToInternal(userKey)

        reply = QtWidgets.QMessageBox.question(
            self,
            translate("DataView", "Confirm clean up"),
            (translate("DataView", "Are you sure you want to erase") + " \"" +
             userKey + "\" " + translate("DataView", "from the stream?")),
            QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes
        )

        if reply == QtWidgets.QMessageBox.Yes:
            if self.__puzzleItem is None:
                del self.__stream[key]
            else:
                self.__data.deleteFromStream(key)

        self.update()

    def __showItemTraceback(self):
        i = self.treeView.selectedIndexes()[0]
        userKey = self.treeView.model().data(i, 0)
        key = self.__translateKeyToInternal(userKey)

        if self.__puzzleItem is not None:
            key = str(self.__puzzleItem.id) + "-" + key

        PSTracebackView(key, userKey, self.__stream, self.__modules, self)

    def __setXDropdown(self):
        index = self.dropdownX.currentIndex()
        if isinstance(self.tableView.model(), PSStandardTableModel):
            if index > 0:
                self.__x = self.tableView.model().modelData[index - 1]
            else:
                self.__x = None
            self.plotUpdate()

    def __setYDropdown(self):
        index = self.dropdownY.currentIndex()
        if isinstance(self.tableView.model(), PSStandardTableModel):
            if index >= 0:
                self.__y = self.tableView.model().modelData[index]
                self.plotUpdate()

    def __swapAxes(self):
        ix, iy = self.dropdownX.currentIndex(), self.dropdownY.currentIndex()
        self.dropdownX.setCurrentIndex(iy + 1)
        self.dropdownY.setCurrentIndex(ix - 1)

    def plotUpdate(self):
        try:
            if (self.__y is not None and
                    isinstance(self.tableView.model(), PSStandardTableModel)):
                y = np.array(self.__y)

                if self.__x is None:
                    x = np.arange(len(self.__y))
                    self.swapBtn.setEnabled(False)
                else:
                    x = np.array(self.__x)
                    self.swapBtn.setEnabled(True)

                types = [int, float, np.int32, np.int64, np.float32,
                         np.float64, "int32", "int64", "float32", "float64"]

                if x.dtype in types and y.dtype in types:
                    self.plotCurve.setData(x, y)

                    if (self.__x is None or
                            len(self.tableView.model().keys) == 0):
                        keyx = "index"
                    else:
                        ind = self.dropdownX.currentIndex() - 1
                        if ind >= len(self.tableView.model().keys):
                            ind = 0
                        keyx = self.tableView.model().keys[ind]

                    ind = self.dropdownY.currentIndex()
                    if ind >= len(self.tableView.model().keys):
                        ind = 0
                    if len(self.tableView.model().keys) > 0:
                        keyy = self.tableView.model().keys[ind]
                    else:
                        keyy = ""

                    self.plotWidget.getPlotItem().setLabel("bottom", keyx)
                    self.plotWidget.getPlotItem().setLabel("left", keyy)
        except Exception as e:
            print(e)

    def treeContextMenu(self, event: QtCore.QEvent):
        menu = QtWidgets.QMenu(self)

        i = self.treeView.selectedIndexes()[0]
        key = self.treeView.model().data(i, 0)

        if self.__translateKeyToInternal(key) in self.__keys:
            if self.__puzzleItem is not None:
                tracebackAction = menu.addAction(
                    translate("DataView", "Show traceback"))
                tracebackAction.triggered.connect(self.__showItemTraceback)
            deleteAction = menu.addAction(
                translate("DataView", "Delete from stream"))
            deleteAction.triggered.connect(self.__deleteItem)

            menu.exec_(self.treeView.mapToGlobal(event))

    def tableContextMenu(self, event: QtCore.QEvent):
        menu = QtWidgets.QMenu(self)
        calculateAction = menu.addAction(
            translate("DataView", "Calculate mean, sum and std."))
        calculateAction.triggered.connect(self.__calculateMeanStd)
        exportAction = menu.addAction(translate("DataView", "Export"))
        exportAction.triggered.connect(self.exportSelected)
        menu.exec_(self.tableView.mapToGlobal(event))

    def showPlotWidget(self):
        self.hideMplWidget()
        self.plotGroupWidget.show()
        self.verticalSplitter.addWidget(self.plotGroupWidget)
        if self.__lastPlotSize is not None:
            s = self.verticalSplitter.sizes()
            self.verticalSplitter.setSizes(
                [sum(s) - self.__lastPlotSize, self.__lastPlotSize])

    def hidePlotWidget(self):
        if len(self.verticalSplitter.sizes()) > 1:
            self.__lastPlotSize = self.verticalSplitter.sizes()[1]
        self.plotGroupWidget.hide()
        self.plotGroupWidget.setParent(None)

    def showMplWidget(self):
        self.hidePlotWidget()
        self.hideMplWidget()
        self.verticalSplitter.addWidget(self.mplGroupWidget)
        self.mplGroupWidget.show()
        if self.__lastPlotSize is not None:
            s = self.verticalSplitter.sizes()
            self.verticalSplitter.setSizes(
                [sum(s) - self.__lastPlotSize, self.__lastPlotSize])

    def hideMplWidget(self):
        if len(self.verticalSplitter.sizes()) > 1:
            self.__lastPlotSize = self.verticalSplitter.sizes()[1]
        self.__closeCurrentMplPlotWidget()
        self.mplGroupWidget.hide()
        self.mplGroupWidget.setParent(None)

    def __closeCurrentMplPlotWidget(self):
        if self.__mplPlotWidget is not None:
            self.__mplPlotWidget.clear()
            plt.close("all")
            self.mplLayout.removeWidget(self.__mplPlotWidget)
            self.__mplPlotWidget.setParent(None)
            self.__mplPlotWidget.hide()
            del self.__mplPlotWidget
            self.__mplPlotWidget = None

        if self.__puzzleItem is not None:
            self.__data.cleanRam()

        gc.collect()

    """
    ===========================================================================
        Selection stuff
    """

    def __tableSelectionChanged(self, selected: list, deselected: list):
        model = self.tableView.model()

        if (isinstance(model, PSStandardTableModel) and
                self.tableView.selectionModel().isRowSelected(
                    0, QtCore.QModelIndex())):
            self.tableView.selectionModel().selectionChanged.disconnect(
                self.__tableSelectionChanged)

            for c in range(model.columnCount()):
                self.tableView.selectionModel().select(
                    model.index(0, c),
                    QtCore.QItemSelectionModel.Deselect
                )

            self.tableView.selectionModel().selectionChanged.connect(
                self.__tableSelectionChanged)

        if (model.rowCount() * model.columnCount() <= 1e5):
            self.__calculateMeanStd()
        else:
            self.statusBarLabel.setText("")

    def __calculateMeanStd(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        model = self.tableView.model()
        data = []

        for ind in self.tableView.selectedIndexes():
            try:
                item = model.getItemAt(ind.row(), ind.column())

                if item is not None:
                    data.append(item)
            except Exception as e:
                print(e)

        try:
            data = np.array(data)
            output = translate("DataView", "Sum") + ": " + str(np.sum(data))
            output += ("; " + translate("DataView", "Mean") + ": " +
                       str(np.mean(data)))

            if len(data) > 1:
                output += ("; " + translate("DataView", "Standard deviation") +
                           ": " + str(np.std(data, ddof=1)))
        except Exception:
            output = ""

        self.statusBarLabel.setText(output)
        QtWidgets.QApplication.restoreOverrideCursor()

    """
    ===========================================================================
        Export
    """

    def exportSelected(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        export = self.__getSelectionArray()
        QtWidgets.QApplication.restoreOverrideCursor()

        if export is not None:
            PSTableExportDialog(export, self)

    def exportCompleteTable(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        export = self.__getTableArray()
        QtWidgets.QApplication.restoreOverrideCursor()

        if export is not None:
            PSTableExportDialog(export, self)

    def __getSelectionArray(self) -> np.ndarray:
        for c in range(self.tableView.model().columnCount()):
            if not self.tableView.selectionModel().isColumnSelected(
                    c, QtCore.QModelIndex()):
                break
        else:
            return self.__getTableArray()

        indices = self.tableView.selectedIndexes()
        countR = [i.row() for i in indices]
        countC = [i.column() for i in indices]

        if len(countR) > 0 and len(countC) > 0:
            minR, minC = min(countR), min(countC)
            maxR, maxC = max(countR), max(countC)
            nR, nC = maxR - minR + 1, maxC - minC + 1

            try:
                data = np.zeros((nR, nC))

                for i in indices:
                    r, c = i.row() - minR, i.column() - minC
                    data[r, c] = self.tableView.model().getItemAt(
                        i.row(), i.column())
                return data
            except Exception:
                pass
            return None

    def __getTableArray(self) -> np.ndarray:
        model = self.tableView.model()

        if self.currentModelType == "2D":
            return model.array
        elif self.currentModelType == "standard":
            maxR, maxC = model.rowCount() - 1, model.columnCount()

            try:
                data = np.zeros((maxR, maxC))
                model = self.tableView.model()

                for r in range(maxR):
                    for c in range(maxC):
                        data[r, c] = model.getItemAt(r + 1, c)
                return data
            except Exception as e:
                print(e)
        return None

    def closeEvent(self, event: QtCore.QEvent):
        self.__close()
        super().closeEvent(event)

    def close(self):
        self.__close()
        super().close()

    def __close(self):
        self.__closeCurrentMplPlotWidget()
        self.setParent(None)
        gc.collect()
        self.closedSignal.emit(self)
