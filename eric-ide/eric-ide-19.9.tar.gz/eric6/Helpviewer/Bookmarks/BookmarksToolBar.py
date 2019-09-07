# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2019 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a tool bar showing bookmarks.
"""

from __future__ import unicode_literals

from PyQt5.QtCore import pyqtSignal, Qt, QUrl, QCoreApplication
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWebKitWidgets import QWebPage

from E5Gui.E5ModelToolBar import E5ModelToolBar

import Helpviewer.HelpWindow

from .BookmarksModel import BookmarksModel


class BookmarksToolBar(E5ModelToolBar):
    """
    Class implementing a tool bar showing bookmarks.
    
    @signal openUrl(QUrl, str) emitted to open a URL in the current tab
    @signal newUrl(QUrl, str) emitted to open a URL in a new tab
    """
    openUrl = pyqtSignal(QUrl, str)
    newUrl = pyqtSignal(QUrl, str)
    
    def __init__(self, mainWindow, model, parent=None):
        """
        Constructor
        
        @param mainWindow reference to the main window (HelpWindow)
        @param model reference to the bookmarks model (BookmarksModel)
        @param parent reference to the parent widget (QWidget)
        """
        E5ModelToolBar.__init__(
            self, QCoreApplication.translate("BookmarksToolBar", "Bookmarks"),
            parent)
        
        self.__mw = mainWindow
        self.__bookmarksModel = model
        
        Helpviewer.HelpWindow.HelpWindow.bookmarksManager()\
            .bookmarksReloaded.connect(self.__rebuild)
        
        self.setModel(model)
        self.setRootIndex(model.nodeIndex(
            Helpviewer.HelpWindow.HelpWindow.bookmarksManager().toolbar()))
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__contextMenuRequested)
        self.activated.connect(self.__bookmarkActivated)
        
        self.setHidden(True)
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        self._build()
    
    def __rebuild(self):
        """
        Private slot to rebuild the toolbar.
        """
        self.__bookmarksModel = \
            Helpviewer.HelpWindow.HelpWindow.bookmarksManager()\
            .bookmarksModel()
        self.setModel(self.__bookmarksModel)
        self.setRootIndex(self.__bookmarksModel.nodeIndex(
            Helpviewer.HelpWindow.HelpWindow.bookmarksManager().toolbar()))
        self._build()
    
    def __contextMenuRequested(self, pos):
        """
        Private slot to handle the context menu request.
        
        @param pos position the context menu shall be shown (QPoint)
        """
        act = self.actionAt(pos)
        menu = QMenu()
        
        if act is not None:
            v = act.data()
            
            if act.menu() is None:
                act2 = menu.addAction(self.tr("Open"))
                act2.setData(v)
                act2.triggered.connect(
                    lambda: self.__openBookmark(act2))
                act2 = menu.addAction(self.tr("Open in New Tab\tCtrl+LMB"))
                act2.setData(v)
                act2.triggered.connect(
                    lambda: self.__openBookmarkInNewTab(act2))
                menu.addSeparator()
            
            act2 = menu.addAction(self.tr("Remove"))
            act2.setData(v)
            act2.triggered.connect(lambda: self.__removeBookmark(act2))
            menu.addSeparator()
            
            act2 = menu.addAction(self.tr("Properties..."))
            act2.setData(v)
            act2.triggered.connect(lambda: self.__edit(act2))
            menu.addSeparator()
        
        menu.addAction(self.tr("Add &Bookmark..."), self.__newBookmark)
        menu.addAction(self.tr("Add &Folder..."), self.__newFolder)
        
        menu.exec_(QCursor.pos())
    
    def __bookmarkActivated(self, idx):
        """
        Private slot handling the activation of a bookmark.
        
        @param idx index of the activated bookmark (QModelIndex)
        """
        assert idx.isValid()
        
        if self._mouseButton == Qt.XButton1:
            self.__mw.currentBrowser().pageAction(QWebPage.Back).trigger()
        elif self._mouseButton == Qt.XButton2:
            self.__mw.currentBrowser().pageAction(QWebPage.Forward).trigger()
        elif self._mouseButton == Qt.LeftButton:
            if self._keyboardModifiers & Qt.ControlModifier:
                self.newUrl.emit(
                    idx.data(BookmarksModel.UrlRole),
                    idx.data(Qt.DisplayRole))
            else:
                self.openUrl.emit(
                    idx.data(BookmarksModel.UrlRole),
                    idx.data(Qt.DisplayRole))
    
    def __openBookmark(self, act):
        """
        Private slot to open a bookmark in the current browser tab.
        
        @param act reference to the triggering action
        @type QAction
        """
        idx = self.index(act)
        
        self.openUrl.emit(
            idx.data(BookmarksModel.UrlRole),
            idx.data(Qt.DisplayRole))
    
    def __openBookmarkInNewTab(self, act):
        """
        Private slot to open a bookmark in a new browser tab.
        
        @param act reference to the triggering action
        @type QAction
        """
        idx = self.index(act)
        
        self.newUrl.emit(
            idx.data(BookmarksModel.UrlRole),
            idx.data(Qt.DisplayRole))
    
    def __removeBookmark(self, act):
        """
        Private slot to remove a bookmark.
        
        @param act reference to the triggering action
        @type QAction
        """
        idx = self.index(act)
        
        self.__bookmarksModel.removeRow(idx.row(), self.rootIndex())
    
    def __newBookmark(self):
        """
        Private slot to add a new bookmark.
        """
        from .AddBookmarkDialog import AddBookmarkDialog
        dlg = AddBookmarkDialog()
        dlg.setCurrentIndex(self.rootIndex())
        dlg.exec_()
    
    def __newFolder(self):
        """
        Private slot to add a new bookmarks folder.
        """
        from .AddBookmarkDialog import AddBookmarkDialog
        dlg = AddBookmarkDialog()
        dlg.setCurrentIndex(self.rootIndex())
        dlg.setFolder(True)
        dlg.exec_()
    
    def _createMenu(self):
        """
        Protected method to create the menu for a tool bar action.
        
        @return menu for a tool bar action (E5ModelMenu)
        """
        from .BookmarksMenu import BookmarksMenu
        menu = BookmarksMenu(self)
        menu.openUrl.connect(self.openUrl)
        menu.newUrl.connect(self.newUrl)
        return menu
    
    def __edit(self, act):
        """
        Private slot to edit a bookmarks properties.
        
        @param act reference to the triggering action
        @type QAction
        """
        from .BookmarkPropertiesDialog import BookmarkPropertiesDialog
        idx = self.index(act)
        node = self.__bookmarksModel.node(idx)
        dlg = BookmarkPropertiesDialog(node)
        dlg.exec_()
