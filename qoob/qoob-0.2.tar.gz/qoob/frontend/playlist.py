#!/usr/bin/python3
import copy
import os
import re
from PyQt5 import QtGui, QtWidgets, QtCore

try:
    from ..__id__ import ID
    from ..backend import parser, tools
    from ..frontend import trinkets
except ValueError:
    from __id__ import ID
    from backend import parser, tools
    from frontend import trinkets


LOCAL_DIR = os.path.dirname(os.path.realpath(__file__)) + "/"
DB_DIR = os.path.expanduser(f"~/.config/{ID}/")
DEFAULT = \
{
    "sort order": QtCore.Qt.AscendingOrder,
    "sort column": 0,
    "column width": {0:200, 1:200, 2:80, 4:80},
    "current": "",
    "files": []
}


class Menu(QtWidgets.QMenu):
    action = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.preferences = parent.preferences
        self.icon = parent.icon
        self.aboutToShow.connect(self._refresh)

    def _refresh(self):
        self.clear()
        if self.parent.copied:
            self.addAction(self.icon["paste"], "Paste selection", lambda: self.action.emit("paste"))

        if self.parent.tabWidget.current.selectedItems():
            self.addAction(self.icon["cut"], "Cut selection", lambda: self.action.emit("cut"))
            self.addAction(self.icon["copy"], "Copy selection", lambda: self.action.emit("copy"))
            if self.preferences.get("general", "file manager"):
                self.addAction(self.icon["folder"], "Browse song folder", lambda: self.action.emit("browse"))
            self.addSeparator()
            self.addAction(self.icon["remove"], "Delete from playlist", lambda: self.action.emit("delete from playlist"))
            self.addAction(self.icon["delete"], "Delete from disk", lambda: self.action.emit("delete prompt"))


class Tabs(QtWidgets.QTabWidget):
    keyEvent = QtCore.pyqtSignal(object, int)
    clearTabPlaylist = QtCore.pyqtSignal(str)
    changed = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.preferences = parent.preferences

        self.addTab(QtWidgets.QWidget(), "Library viewer")
        self.addTab(QtWidgets.QWidget(), "")

        self.setDocumentMode(True)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setTabEnabled(1, False)
        self.dummyButton = QtWidgets.QPushButton()
        self.dummyButton.setFixedSize(0, 0)
        self.newButton = QtWidgets.QPushButton()
        self.newButton.setFlat(True)
        self.newButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.newButton.setFixedSize(30, 20)
        self.newButton.clicked.connect(self._add)
        self.newButton.setToolTip("New playlist")
        self.tabBar().setTabButton(0, QtWidgets.QTabBar.RightSide, self.dummyButton)
        self.tabBar().setTabButton(1, QtWidgets.QTabBar.RightSide, self.newButton)
        self.tabBar().setChangeCurrentOnDrag(True)
        self.tabBar().setAcceptDrops(True)

        self.tabCloseRequested.connect(self._close)
        self.currentChanged.connect(self._changed)
        self.installEventFilter(self)
        self.tabBar().installEventFilter(self)

        self.tabs = {}
        self.tabs["Library viewer"] = Tree(parent)
        self.current = self.tabs["Library viewer"]
        self.initStyle()

        self.viewLayout = QtWidgets.QGridLayout()
        self.viewLayout.addWidget(self.tabs["Library viewer"])
        self.currentWidget().setLayout(self.viewLayout)

        self.playlist = tools.Database("playlist")
        self._playlistsInit()
        self._playlistsLoadAttributes()
        self._playlistsLoadContent()

    def eventFilter(self, obj, event):
        if obj == self.tabBar() and event.type() == QtCore.QEvent.MouseButtonDblClick:
            self._rename()
        elif obj == self and event.type() == QtCore.QEvent.ShortcutOverride:
            self.keyEvent.emit(event.modifiers(), event.key())
        return QtCore.QObject.event(obj, event)

    def _add(self, name=None):
        layout = QtWidgets.QVBoxLayout()
        tab = QtWidgets.QWidget(self)
        count = self.tabBar().count()
        index = 1
        if not name:
            name = "Playlist " + str(index)
        while name in self.tabs:
            index += 1
            name = "Playlist " + str(index)

        self.tabs[name] = {}
        self.tabs[name] = Tree(self.parent)
        header = self.tabs["Library viewer"].header()
        for column in range(5):
            self.tabs[name].setColumnWidth(column, header.sectionSize(column))

        sortOrder = header.sortIndicatorOrder()
        sortColumn = self.tabs["Library viewer"].sortColumn()
        self.tabs[name].sortByColumn(sortColumn, sortOrder)

        self.addTab(tab, name)
        self.setCurrentWidget(tab)
        self.tabBar().moveTab(count - 1, count)
        self.currentWidget().setLayout(layout)
        layout.addWidget(self.tabs[name])

    def _changed(self, index):
        tabName = self.tabText(index)
        tabName = tabName.lstrip("&")  # KDE bug fix (auto append of &)
        if tabName:
            self.current = self.tabs[tabName]
            self.changed.emit()

    def _close(self, tab):
        tabName = self.tabText(tab)
        tabName = tabName.lstrip("&")  # KDE bug fix (auto append of &)
        tabHasItems = self.tabs[tabName].topLevelItemCount()
        if tabHasItems:
            self._deletePrompt(tab, tabName)
        else:
            self._delete(tab, tabName)

    def _delete(self, tab, tabName):
        del self.tabs[tabName]
        if tabName in self.playlist.db:
            del self.playlist.db[tabName]
            self.playlist.save()
        self.removeTab(tab)
        self.clearTabPlaylist.emit(tabName)

        # Prevent landing on the '+' tab
        currentIndex = self.tabBar().currentIndex()
        if not self.tabText(currentIndex):
            for i in range(self.tabBar().count()):
                if self.tabText(i) == "Library viewer":
                    self.tabBar().setCurrentIndex(i)
                    break

    def _deletePrompt(self, tab, tabName):
        msg = trinkets.DeletePrompt()
        msg.setText(f"Please confirm deletion of playlist '{tabName}'")
        if msg.exec_() == QtWidgets.QMessageBox.Apply:
            self._delete(tab, tabName)

    def _playlistDumpAttributes(self, tabName):
        self.playlist.db[tabName]["sort order"] = self.tabs[tabName].header().sortIndicatorOrder()
        self.playlist.db[tabName]["sort column"] = self.tabs[tabName].sortColumn()
        for column in (0, 1, 2, 4):
            width = self.tabs[tabName].header().sectionSize(column)
            self.playlist.db[tabName]["column width"][column] = width

    def _playlistDumpFiles(self, tabName):
        if self.tabs[tabName].currentItem():
            self.playlist.db[tabName]["current"] = self.tabs[tabName].currentItem().text(5)

        for item in range(self.tabs[tabName].topLevelItemCount()):
            item = self.tabs[tabName].topLevelItem(item)
            self.playlist.db[tabName]["files"].append(item.text(5))

    def _playlistsInit(self):
        for tabName in self.playlist.db:
            if not tabName == "Library viewer":
                self._add(tabName)

    def _playlistsLoadAttributes(self):
        for tabName in self.playlist.db:
            sortOrder = self.playlist.db[tabName].get("sort order", DEFAULT["sort order"])
            sortColumn = self.playlist.db[tabName].get("sort column", DEFAULT["sort column"])
            columnWidth = self.playlist.db[tabName].get("column width", DEFAULT["column width"])
            self.tabs[tabName].sortByColumn(sortColumn, sortOrder)
            for column in columnWidth:
                self.tabs[tabName].setColumnWidth(int(column), columnWidth[column])

    def _playlistsLoadContent(self):
        for tabName in self.playlist.db:
            for path in self.playlist.db[tabName]["files"]:
                item = self.tabs[tabName].add(path, append=True)
                if "current" in self.playlist.db[tabName] and path == self.playlist.db[tabName]["current"]:
                    self.tabs[tabName].setCurrentItem(item)
        self.tabBar().setCurrentIndex(self.preferences.get("state", "tab"))

    def _rename(self):
        tabIndex = self.tabBar().currentIndex()
        oldName = self.tabText(tabIndex)
        oldName = oldName.lstrip("&")  # KDE bug fix (auto append of &)
        if not oldName == "Library viewer":
            newName = self._renamePrompt(oldName)
            if newName and newName not in self.tabs:
                self.tabs[newName] = self.tabs.pop(oldName)
                if oldName in self.playlist.db:
                    self.playlist.db[newName] = self.playlist.db.pop(oldName)
                    self.playlist.save()
                self.setTabText(tabIndex, newName)

    def _renamePrompt(self, oldName):
        msg = QtWidgets.QInputDialog()
        msg.setInputMode(QtWidgets.QInputDialog.TextInput)
        msg.setWindowFlags(msg.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        msg.setWindowTitle(f"Rename '{oldName}'")
        msg.setLabelText("Enter the new name:")
        msg.setTextValue(oldName)
        msg.setFixedSize(250, 100)
        accept = msg.exec_()
        newName = msg.textValue()
        newName = newName.replace("&", "")  # KDE bug fix
        if accept and newName:
            return newName

    def initStyle(self):
        iconTheme = self.preferences.get("general", "icon theme")
        iconPath = f"{LOCAL_DIR}../icons/{iconTheme}/"
        stylesheet = f"QTabBar::close-button {{ image: url({iconPath}tab_close.svg); }}\n"
        stylesheet += f"QTabBar::close-button:hover {{ image: url({iconPath}tab_hover.svg); }}\n"
        self.setStyleSheet(stylesheet)
        self.newButton.setIcon(self.parent.icon["tab_add"])

    def playlistSave(self):
        for index in range(self.count() - 1):
            tabName = self.tabText(index)
            tabName = tabName.lstrip("&")  # KDE bug fix (auto append of &)
            self.playlist.db[tabName] = copy.deepcopy(DEFAULT)
            self._playlistDumpAttributes(tabName)
            self._playlistDumpFiles(tabName)
        self.playlist.save()


class Tree(QtWidgets.QTreeWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.preferences = parent.preferences
        self.metadata = parent.parser.metadata
        self.setHeaderLabels(["Artist", "Album", "Track", "Title", "Duration", "__path__"])
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(False)
        self.setColumnWidth(5, 0)  # Hide __path__ column
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)  # DragDrop does not catch files drop
        self.customContextMenuRequested.connect(parent.menuShow)
        self.itemDoubleClicked.connect(parent.player.activateSelection)

        header = self.header()
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        header.setStretchLastSection(False)
        header.setSortIndicatorShown(True)
        header.setSectionsClickable(True)
        header.setMinimumSectionSize(0)
        header.sectionClicked.connect(self._headerClickEvent)

    def _dropFromFiles(self, event):
        self.clearSelection()
        for url in event.mimeData().urls():
            path = url.toString(QtCore.QUrl.PreferLocalFile)
            path = self._translateHexCodes(path)
            if os.path.isfile(path):
                self.add(path, select=True)
            elif os.path.isdir(path):
                for root, subfolder, files in os.walk(path):
                    for f in files:
                        self.add(f"{root}/{f}", select=True)

    def _dropFromPlaylist(self, event):
        items = self._mimeParse(event)
        if items:
            self.clearSelection()
            paths = self._mimeExtract(items, 5)
            for path in paths:
                self.add(path, select=True)

    def _dropFromTree(self, event):
        items = self._mimeParse(event)
        if items:
            self.clearSelection()
            paths = self._mimeExtract(items, 1)
            for path in paths:
                for root, subfolder, files in os.walk(path):
                    for f in files:
                        self.add(f"{root}/{f}", select=True)

    def _mimeDecode(self, data):
        result = []
        stream = QtCore.QDataStream(data)
        while not stream.atEnd():
            item = {}
            item['row'] = stream.readInt32()
            item['col'] = stream.readInt32()
            for role in range(stream.readInt32()):
                key = QtCore.Qt.ItemDataRole(stream.readInt32())
                value = stream.readQVariant()
            if key == QtCore.Qt.DisplayRole:
                item['value'] = value
                result.append(item)
        return result

    def _mimeExtract(self, items, column):
        paths = []
        for item in items:
            if item["col"] == column:
                paths.append(item["value"])
        return paths

    def _mimeParse(self, event):
        data = event.mimeData()
        format = 'application/x-qabstractitemmodeldatalist'
        if data.hasFormat(format):
            formatedData = data.data(format)
            items = self._mimeDecode(formatedData)
            return items
        return None

    def _translateHexCodes(self, string):
        """Find and replace hex codes from a string
        Replace '%5BFF1~10%5D.mp3 %21' to '[FF1~10].mp3 !'
        """
        # %\d{2}       Patterns starting with a %, followed by two digit
        # %\d[a-fA-F]  Patterns starting with a %, followed by one digit and one letter from a to F
        hexChars = re.findall(r"%\d{2}|%\d[a-fA-F]", string)
        for code in hexChars:
            litteral = code.replace("%", "0x")
            litteral = chr(eval(litteral))
            string = string.replace(code, litteral)
        return string

    def dragEnterEvent(self, event):
        isFiles = event.mimeData().hasUrls()
        isTreeItem = event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist")
        if isTreeItem or isFiles:
            event.acceptProposedAction()
        QtWidgets.QTreeWidget.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        item = self.itemAt(event.pos())
        if item:
            if event.source() != self:
                self.setCurrentItem(item)
        QtWidgets.QTreeWidget.dragMoveEvent(self, event)

    def dropEvent(self, event):
        if event.source() == self:
            event.setDropAction(QtCore.Qt.MoveAction)

        elif event.source() == self.parent.library:
            self._dropFromTree(event)

        elif isinstance(event.source(), Tree):
            self._dropFromPlaylist(event)

        elif event.mimeData().hasUrls():
            self._dropFromFiles(event)

        self.setFocus(True)
        QtWidgets.QTreeWidget.dropEvent(self, event)

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            self.parent.player.activateSelection()

        # Block default behavior (lateral tree scrolling)
        if not key == QtCore.Qt.Key_Left and not key == QtCore.Qt.Key_Right:
            QtWidgets.QTreeWidget.keyPressEvent(self, event)

    def _headerClickEvent(self, i):
        self.setSortingEnabled(True)
        self.setSortingEnabled(False)
        header = self.header()
        header.setSortIndicatorShown(True)
        header.setSectionsClickable(True)

    def add(self, path, append=False, select=False):
        basename = os.path.basename(path)
        extension = os.path.splitext(basename)[1].lower()
        if extension in parser.ALLOWED_AUDIO_TYPES:
            tags = self.parent.parser.header(path)
            item = TreeItem()
            item.setText(0, tags["artist"])
            item.setText(1, tags["album"])
            item.setText(2, tags["track"])
            item.setText(3, tags["title"])
            item.setText(4, tags["duration"])
            item.setText(5, path)

            if append:
                self.addTopLevelItem(item)
            else:
                ## Bottleneck?
                index = self.currentIndex().row()
                if index == -1: index = 0
                self.insertTopLevelItem(index, item)
            item.setSelected(select)
            return item
        return None


class TreeItem(QtWidgets.QTreeWidgetItem):
    def __init__(self):
        super().__init__()
        self.setFlags(self.flags() &~ QtCore.Qt.ItemIsDropEnabled)
        self.lastColor = "none"

    def __lt__(self, other):
        column = self.treeWidget().sortColumn()
        key1 = self.text(column)
        key2 = other.text(column)
        try:
            return int(key1) < int(key2)
        except ValueError:
            return key1.lower() < key2.lower()

    def setColor(self, color):
        priority = {"none": 0, "green": 0, "yellow": 1, "red": 2}
        if priority[color] >= priority[self.lastColor]:
            self.lastColor = color
            try:
                for column in range(5):
                    if color == "none":
                        self.setData(column, QtCore.Qt.BackgroundRole, None)
                        self.setData(column, QtCore.Qt.ForegroundRole, None)
                    elif color == "green":
                        self.setForeground(column, QtGui.QColor("#004000"))
                        self.setBackground(column, QtGui.QColor("#c6efce"))
                    elif color == "yellow":
                        self.setForeground(column, QtGui.QColor("#553400"))
                        self.setBackground(column, QtGui.QColor("#ffeb9c"))
                    elif color == "red":
                        self.setForeground(column, QtGui.QColor("#9c0006"))
                        self.setBackground(column, QtGui.QColor("#ffc7ce"))
            except RuntimeError:
                pass
