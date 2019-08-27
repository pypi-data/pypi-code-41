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

from Qt.QtCore import *
from Qt.QtWidgets import *


import artellapipe
from artellapipe.tools.assetsmanager.core import assetsmanager

from plottwist.core import userinfo
from plottwist.pipeline.tools.assetsmanager.widgets import assetswidget
from plottwist.pipeline.kitsu import loginwidget


class PlotTwistAssetsManager(assetsmanager.ArtellaAssetsManager, object):

    USER_INFO_CLASS = userinfo.PlotTwistUserInfo
    ASSET_WIDGET_CLASS = assetswidget.PlotTwistAssetsWidget

    def __init__(self):
        super(PlotTwistAssetsManager, self).__init__(
            project=artellapipe.plottwist, auto_start_assets_viewer=False
        )

        self._kitsu_store = False
        self._kitsu_user_data = None

        self._menu_bar.setVisible(False)

        self._try_kitsu_login()

    def ui(self):
        super(PlotTwistAssetsManager, self).ui()

        self._kitsu_login_widget = loginwidget.KitsuLoginWidget()

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

        self._main_stack.addWidget(self._kitsu_login_widget)
        self._main_stack.addWidget(no_kitsu_log_widget)

    def setup_signals(self):
        super(PlotTwistAssetsManager, self).setup_signals()

        self._user_info.login.connect(self._on_kitsu_login)
        self._user_info.logout.connect(self._on_kitsu_logout)

    def _setup_menubar(self):
        """
        Overrides base ArtellaManager _setup_menubar function
        """

        menubar_widget = super(PlotTwistAssetsManager, self)._setup_menubar()

        self._project_kitsu_btn = QToolButton(self)
        self._project_kitsu_btn.setText('Kitsu')
        self._project_kitsu_btn.setIcon(artellapipe.plottwist.resource.icon('kitsu'))
        self._project_kitsu_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self._project_kitsu_btn.setVisible(False)
        self._project_kitsu_btn.clicked.connect(self._on_open_project_in_kitsu)

        menubar_widget.layout().addWidget(self._project_kitsu_btn, 0, 3, 1, 1, Qt.AlignCenter)

        return menubar_widget

    def _update_types(self):
        """
        Internal function that updates current asset types with the info retrieve from Kitsu
        """

        self._project.update_entity_types_from_kitsu(force=True)
        asset_types = self._project.update_types_from_kitsu(force=True)
        category_names = [asset_type.name for asset_type in asset_types]
        self._assets_widget.update_asset_categories(category_names)

    def _try_kitsu_login(self):
        """
        Internal function that tries to login into Kitsu
        """

        valid_login = self._user_info.try_kitsu_login()
        if not valid_login:
            self._main_stack.slide_in_index(2)

    def _on_open_project_in_kitsu(self):
        """
        Internal callback function that is called when the user presses on Kitsu button in menu bar
        """

        if not self._project:
            return

        self._project.open_in_kitsu()

    def _on_kitsu_login(self):
        self._update_types()
        self._assets_widget.update_assets()
        self._main_stack.slide_in_index(0)
        self.show_ok_message('Successfully logged into Kitsu')

    def _on_kitsu_logout(self):
        self._main_stack.slide_in_index(2)
        self._assets_widget.clear_assets()
        self.show_ok_message('Successfully logged out from Kitsu')

    # def _kitsu_login(self, data):
    #     """
    #     Internal function that is called by Kitsu Worker to execute login
    #     :param data:
    #     :return:
    #     """
    #
    #     kitsu_user = self._project.kitsu_user
    #     kitsu_password = self._project.kitsu_password
    #
    #     if not kitsu_user or not kitsu_password:
    #         artellapipe.plottwist.logger.warning('Impossible to login into Kitsu because user and password are not given!')
    #         return
    #
    #     valid_login = artellapipe.plottwist.login_kitsu(kitsu_user, kitsu_password)
    #     self._user_info.update_kitsu_status()
    #     if valid_login:
    #         self._update_types()
    #         return True
    #     else:
    #         self._main_stack.slide_in_index(2)
    #         return False
    #
    # def _on_kitsu_login_accepted(self, email, password, store_credentials):
    #     """
    #     Internal callback function that is called when the user successfully log into Kitsu through Kitsu login form
    #     :param email: variant, str or None
    #     :param password: variant, str or None
    #     :param store_credentials: bool
    #     """
    #
    #     self._enable_kitsu(email, password, store_credentials)
    #
    # def _on_kitsu_worker_completed(self, uid, valid_login):
    #     """
    #     Internal callback function that is called when Kitsu worker finishes
    #     :param uid: str
    #     :param valid_login: bool
    #     """
    #
    #     self._main_stack.slide_in_index(0)
    #     self._user_info.setVisible(True)
    #     if valid_login:
    #         if not self._project.is_logged_in_kitsu():
    #             artellapipe.plottwist.logger.warning('Something when wrong during Kitsu login')
    #             return
    #         self.show_ok_message('Successfully logged into Kitsu')
    #         if self._project.kitsu_user and self._project.kitsu_pass:
    #             self.settings().set('kitsu_email', self.kitsu_password)
    #             self.settings().set('kitsu_password', self._kitsu_pass)
    #             self.settings().set('kitsu_store_credentials', bool(self._kitsu_store))
    #         self._project_kitsu_btn.setVisible(True)
    #         self._assets_widget.update_assets()
    #     else:
    #         self._user_info.update_kitsu_status()
    #         self._assets_widget.clear_assets()
    #         self._main_stack.slide_in_index(2, force=True)
    #         self.show_error_message('Error while login into Kitsu. Try again please!')
    #
    # def _on_kitsu_worker_failure(self, uid, msg):
    #     """
    #     Internal callback function that is called when Kitsu worker fails
    #     :param uid: str
    #     :param msg: str
    #     """
    #
    #     self._project.kitsu_user = None
    #     self._project.kitsu_password = None
    #     self._kitsu_store = False
    #     self.show_error_message('{} | {}'.format(uid, msg))
    #     artellapipe.logger.error('{} | {}'.format(uid, msg))
    #     self._main_stack.slide_in_index(0)
    #     self._user_info.setVisible(True)


def run():
    win = PlotTwistAssetsManager()
    win.show()

    return win
