#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool that allow artists to interact with Artella functionality inside DCCS in Plot Twist
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
from functools import partial

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDccLib as tp

from tpQtLib.widgets import stack

import artellapipe
from artellapipe.gui import window, button
from artellapipe.tools.assetslibrary import assetslibrary

from plottwist.core import userinfo


class PlotTwistAssetsLibraryWidget(assetslibrary.ArtellaAssetsLibraryWidget, object):

    name = 'PlotTwistAssetsLibrary'
    title = 'Plot Twist - Assets Viewer'

    def __init__(self, project, parent=None):
        super(PlotTwistAssetsLibraryWidget, self).__init__(project=project, parent=parent)

        self._try_kitsu_login()

    def ui(self):
        super(PlotTwistAssetsLibraryWidget, self).ui()

        self._user_info = userinfo.PlotTwistUserInfo(project=artellapipe.plottwist)
        self.main_layout.addWidget(self._user_info)

        self._main_stack = stack.SlidingStackedWidget()
        self.main_layout.addWidget(self._main_stack)

        no_kitsu_log_widget = QFrame()
        no_kitsu_log_widget.setFrameShape(QFrame.StyledPanel)
        no_kitsu_log_widget.setFrameShadow(QFrame.Sunken)
        no_kitsu_log_layout = QVBoxLayout()
        no_kitsu_log_layout.setContentsMargins(0, 0, 0, 0)
        no_kitsu_log_layout.setSpacing(0)
        no_kitsu_log_widget.setLayout(no_kitsu_log_layout)
        no_items_lbl = QLabel()
        no_items_pixmap = artellapipe.plottwist.resource.pixmap('kitsu_no_login')
        no_items_lbl.setPixmap(no_items_pixmap)
        no_items_lbl.setAlignment(Qt.AlignCenter)
        no_kitsu_log_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Preferred, QSizePolicy.Expanding))
        no_kitsu_log_layout.addWidget(no_items_lbl)
        no_kitsu_log_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Preferred, QSizePolicy.Expanding))

        self._main_stack.addWidget(no_kitsu_log_widget)
        self._main_stack.addWidget(self._main_widget)

        self._user_info.login.connect(self._on_kitsu_login)
        self._user_info.logout.connect(self._on_kitsu_logout)

    def _try_kitsu_login(self):
        """
        Internal function that tries to login into Kitsu
        """

        valid_login = self._user_info.try_kitsu_login()
        if valid_login:
            self._assets_viewer.update_assets()
            return True

        return False

    def _on_kitsu_login(self):
        self._assets_viewer.update_assets()
        self._main_stack.slide_in_index(1)

    def _on_kitsu_logout(self):
        self._main_stack.slide_in_index(0)
        self._assets_viewer.clear_assets()

        # self._update_assets_status()

    # def _update_assets_status(self):
    #     """
    #     Internal function that checks asset availability an enables sync button if necessary
    #     """
    #
    #     for i in range(self._assets_viewer.rowCount()):
    #         for j in range(self._assets_viewer.columnCount()):
    #             item = self._assets_viewer.cellWidget(i, j)
    #             if not item:
    #                 continue
    #             asset_widget = item.containedWidget
    #             rig_file_type = asset_widget.asset.get_file_type(defines.SOLSTICE_RIG_ASSET_TYPE)
    #             if rig_file_type:
    #                 published_path = rig_file_type.get_latest_local_published_path()
    #                 if published_path and os.path.isfile(published_path):
    #                     continue
    #             self._create_sync_button(item)
    #
    # def _create_sync_button(self, item):
    #     """
    #     Internal function that creates a sync button in the given item
    #     :param item: ArtellaAssetWidget
    #     """
    #
    #     sync_icon = artellapipe.solstice.resource.icon('sync')
    #     sync_hover_icon = artellapipe.solstice.resource.icon('sync_hover')
    #     sync_btn = button.IconButton(icon=sync_icon, icon_hover=sync_hover_icon, icon_min_size=50)
    #     sync_btn.setIconSize(QSize(50, 50))
    #     sync_btn.move(item.width() * 0.5 - sync_btn.width() * 0.5, item.height() * 0.5 - sync_btn.height() * 0.5)
    #     sync_btn.setParent(item.containedWidget)
    #
    #     not_published_pixmap = artellapipe.solstice.resource.pixmap('asset_not_published')
    #     not_published_lbl = QLabel()
    #     not_published_lbl.move(9, 9)
    #     not_published_lbl.setFixedSize(65, 65)
    #     not_published_lbl.setPixmap(not_published_pixmap)
    #     not_published_lbl.setParent(item.containedWidget)
    #
    #     asset_widget = item.containedWidget
    #     sync_btn.clicked.connect(partial(asset_widget.asset.sync_latest_published_files, None, True))


class PlotTwistAssetsLibrary(assetslibrary.ArtellaAssetsLibrary, object):

    LIBRARY_WIDGET = PlotTwistAssetsLibraryWidget

    def __init__(self, project, parent=None):
        super(PlotTwistAssetsLibrary, self).__init__(project=project, parent=parent)


def run():
    if tp.is_maya():
        win = window.dock_window(project=artellapipe.plottwist, window_class=PlotTwistAssetsLibraryWidget)
        return win
    else:
        win = PlotTwistAssetsLibrary(project=artellapipe.plottwist)
        win.show()
        return win
