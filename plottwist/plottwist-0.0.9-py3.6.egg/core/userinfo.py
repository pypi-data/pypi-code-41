#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains widget implementation that shows user info for Plot Twist
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

from tpQtLib.core import qtutils

import artellapipe
from artellapipe.core import userinfo

from plottwist.pipeline.kitsu import logindialog, userballoon


class PlotTwistUserInfo(userinfo.UserInfo, object):

    login = Signal()
    logout = Signal()

    def __init__(self, project, parent=None):
        super(PlotTwistUserInfo, self).__init__(
            project=project if project else artellapipe.plottwist,
            parent=parent
        )

        self.main_layout.addSpacerItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))

        shutdown_icon = artellapipe.plottwist.resource.icon('shutdown')
        self._kitsu_off_icon = artellapipe.plottwist.resource.icon('kitsu_off')
        self._kitsu_on_icon = artellapipe.plottwist.resource.icon('kitsu_on')

        self._kitsu_btn = QPushButton('Kitsu')
        self._kitsu_btn.setIconSize(QSize(50, 50))
        self._kitsu_btn.setFixedHeight(25)
        self._kitsu_btn.setMinimumWidth(90)
        self._kitsu_btn.setFlat(True)

        self._kitsu_logout_btn = QPushButton()
        self._kitsu_logout_btn.setVisible(False)
        self._kitsu_logout_btn.setIcon(shutdown_icon)
        self._kitsu_btn.setFlat(True)

        self.main_layout.addWidget(self._kitsu_btn)
        self.main_layout.addWidget(self._kitsu_logout_btn)

        self._kitsu_btn.clicked.connect(self._on_open_kitsu_login)
        self._kitsu_logout_btn.clicked.connect(self._on_kitsu_logout)

        self.update_kitsu_status()

    def try_kitsu_login(self):
        """
        Function that tries to log into Kitsu
        """

        valid_login = self._project.login_kitsu()
        if valid_login:
            self._kitsu_login()
            return True

        return False

    def update_kitsu_status(self):
        """
        Synchronizes current Kitsu status between UserInfo and current project
        """

        if not self._project:
            artellapipe.plottwist.logger.warning('Impossible to update Kitsu Status because Project is not defined!')
            return

        if self._project.is_logged_in_kitsu():
            self._kitsu_btn.setIcon(self._kitsu_on_icon)
            self._kitsu_logout_btn.setVisible(True)
        else:
            self._kitsu_btn.setIcon(self._kitsu_off_icon)
            self._kitsu_logout_btn.setVisible(False)

    def _kitsu_login(self):
        """
        Tries to login into Kitsu
        """

        self.update_kitsu_status()
        self.login.emit()

    def _on_open_kitsu_login(self):
        """
        Internal callback function that is called when the user presses the Kitsu button
        """

        if artellapipe.plottwist.is_logged_in_kitsu():
            self._ballon = userballoon.KitsuUserBalloon()
            rect_btn = self._kitsu_btn.geometry()
            rect_balloon = self._ballon.geometry()

            pos = QCursor.pos()
            pos.setX(pos.x() - (self._kitsu_btn.width() / 2) - 20)

            rect_balloon.setRect(
                pos.x(), pos.y(), rect_btn.width(), rect_btn.height()
            )

            self._ballon.setGeometry(rect_balloon)
            self._ballon.show()

        else:
            login_dialog = logindialog.KitsuLoginDialog(project=self._project)
            login_dialog.validLogin.connect(self._on_kitsu_login)
            # login_dialog.invalidLogin.connect(self._on_kitsu_logout)
            login_dialog.exec_()

    def _on_kitsu_login(self):
        """
        Internal callback function that is claled when the user presses the login button
        """

        self._kitsu_login()

    def _on_kitsu_logout(self):
        """
        Internal callback function that is called when the user presses the logout button
        """

        remove_credentials = False
        res = qtutils.show_question(self, 'Kitsu Logout', 'Do you want to remove Kitsu stored credentials?')
        if res == QMessageBox.Yes:
            remove_credentials = True

        valid = artellapipe.plottwist.logout_kitsu(remove_credentials=remove_credentials)
        if not valid:
            artellapipe.plottwist.logger.warning('Error while logging out from Kitsu')
            artellapipe.plottwist.logger.warning('Something when wrong during Kitsu login out')
            return

        self.update_kitsu_status()
        self.logout.emit()
