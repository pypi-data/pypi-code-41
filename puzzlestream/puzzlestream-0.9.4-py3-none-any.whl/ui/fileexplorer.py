import mimetypes
import os
from enum import Enum, auto

from puzzlestream.backend.signal import PSSignal
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

translate = QCoreApplication.translate


class FileAction(Enum):

    OPEN = auto()
    CUT = auto()
    COPY = auto()
    PASTE = auto()
    RENAME = auto()
    DELETE = auto()


class PSFileExplorer(QWidget):

    def __init__(self, parent: QWidget = None):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WA_Hover)
        self.__layout = QHBoxLayout()
        self.__treeView = PSExplorerTreeView(self)
        self.__layout.addWidget(self.__treeView)
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__label = QLabel(">")
        self.__layout.addWidget(self.__label)
        self.__treeView.hide()
        self.setStyleSheet("QWidget { min-width: 0.7em; max-width: 0.7em; }")
        self.setLayout(self.__layout)
        self.__openFileSignal = PSSignal()
        self.__treeView.reactionSignal = self.openFileSignal

    @property
    def openFileSignal(self) -> PSSignal:
        return self.__openFileSignal

    def setPath(self, path: str = None):
        if path is not None:
            model = QFileSystemModel(self)
            model.setNameFilterDisables(True)
            # model.setNameFilters(["*.py"])
            model.setRootPath(os.path.normpath(path))
            self.__treeView.setModel(model)
            self.__treeView.setRootIndex(model.index(os.path.normpath(path)))
            self.__treeView.setSortingEnabled(True)
            self.__treeView.sortByColumn(0, Qt.AscendingOrder)
            self.__treeView.setColumnHidden(1, True)
            self.__treeView.setColumnHidden(2, True)
            self.__treeView.setColumnHidden(3, True)
            self.__treeView.header().hide()
            self.__treeView.setSelectionMode(QTreeView.ExtendedSelection)
            self.__treeView.customContextMenuRequested.connect(
                self.__contextMenuRequested)
            self.__allowShowHide = True

    def selectFile(self, path: str):
        idx = self.__treeView.model().index(path)
        if idx is not None:
            self.__treeView.setCurrentIndex(idx)

    def enterEvent(self, event):
        if self.__allowShowHide:
            self.__label.hide()
            self.__treeView.show()
            self.setStyleSheet(
                "QWidget { min-width: 15em; max-width: 15em; }")
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.__allowShowHide:
            self.__treeView.hide()
            self.__label.show()
            self.setStyleSheet(
                "QWidget { min-width: 0.7em; max-width: 0.7em; }")
        super().leaveEvent(event)

    def __contextMenuRequested(self, point: QPoint):
        self.__allowShowHide = False
        indices = self.__treeView.selectedIndexes()

        if len(indices) > 0:
            menu = QMenu()
            action = menu.addAction(translate("FileExplorer", "Open"))
            action.triggered.connect(
                lambda: self.__fileAction(FileAction.OPEN, indices))
            action = menu.addAction(translate("FileExplorer", "Cut"))
            action.triggered.connect(
                lambda: self.__fileAction(FileAction.CUT, indices))
            action = menu.addAction(translate("FileExplorer", "Copy"))
            action.triggered.connect(
                lambda: self.__fileAction(FileAction.COPY, indices))
            action = menu.addAction(translate("FileExplorer", "Rename"))
            action.triggered.connect(
                lambda: self.__fileAction(FileAction.RENAME, indices))
            action = menu.addAction(translate("FileExplorer", "Delete"))
            action.triggered.connect(
                lambda: self.__fileAction(FileAction.DELETE, indices))
            menu.exec_(self.__treeView.viewport().mapToGlobal(point))
        else:
            menu = QMenu()
            action = menu.addAction(translate("FileExplorer", "Paste"))
            action.triggered.connect(
                lambda: self.__fileAction(FileAction.PASTE))
            menu.exec_(self.__treeView.viewport().mapToGlobal(point))

        self.__allowShowHide = True

    def __fileAction(self, action: FileAction, indices: list = None):
        if indices is not None and len(indices) > 0:
            paths = [str(self.__treeView.model().data(i)) for i in indices]
            absPaths = [os.path.abspath(p) for p in paths]

            if action is FileAction.OPEN:
                self.openFileSignal.emit(paths[0])
            elif action is FileAction.COPY:
                urls = []
                for p in absPaths:
                    urls.append(QUrl.fromLocalFile(p))
                data = QMimeData()
                data.setUrls(urls)
                QApplication.clipboard().setMimeData(data)

        # print(action, indices)


class PSExplorerTreeView(QTreeView):

    reactionSignal = None

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            ind = self.indexAt(event.pos())
            if ind is not None:
                path = str(self.model().data(ind))
                if (os.path.isfile(path) and
                        mimetypes.guess_type(path)[0] == "text/x-python"):
                    self.reactionSignal.emit(path)
        super().mouseReleaseEvent(event)
