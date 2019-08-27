#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementation for Kitsu User Balloon
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from Qt.QtWidgets import *

from tpQtLib.widgets import balloon

import artellapipe


class KitsuUserBalloon(balloon.BalloonDialog, object):
    def __init__(self, parent=None):
        super(KitsuUserBalloon, self).__init__(parent)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        user_info = artellapipe.plottwist.kitsu_user_data()

        full_name_lbl = QLabel('{} - {}'.format(user_info.full_name, user_info.role))
        email_lbl = QLabel(user_info.email)
        timezone_lbl = QLabel('{} - {}'.format(user_info.locale, user_info.timezone))

        main_layout.addWidget(full_name_lbl)
        main_layout.addWidget(email_lbl)
        main_layout.addWidget(timezone_lbl)





