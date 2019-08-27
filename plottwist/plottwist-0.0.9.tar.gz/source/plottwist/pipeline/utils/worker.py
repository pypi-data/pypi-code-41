#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementation for background workers
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from Qt.QtCore import *
from Qt.QtGui import *

import os

import artellapipe

from plottwist.pipeline.kitsu import kitsulib


class KitsuImageDownloaderWorker(QRunnable, object):

    class KitsuImageDownloaderWorkerSignals(QObject, object):
        triggered = Signal(object)

    def __init__(self, *args):
        super(KitsuImageDownloaderWorker, self).__init__(*args)

        self._path = None
        self._preview_id = None
        self.signals = KitsuImageDownloaderWorker.KitsuImageDownloaderWorkerSignals()

    def set_preview_id(self, preview_id):
        """
        Sets the preview ID linked to Kitsu project
        :param preview_id: str
        """

        self._preview_id = preview_id

    def set_path(self, path):
        """
        Sets the path where image should be downloaded
        :param path: str
        """

        self._path = path

    def run(self):
        try:
            if self._preview_id and self._path:
                if not os.path.isfile(self._path):
                    kitsulib.download_preview_file_thumbnail(self._preview_id, self._path)
                if not os.path.isfile(self._path):
                    icon = None
                else:
                    icon_pixmap = QPixmap(self._path)
                    icon = QIcon(icon_pixmap)
                self.signals.triggered.emit(icon)
        except Exception as e:
            artellapipe.plottwist.logger.error('Cannot load thumbnail image: {}!'.format(e))
