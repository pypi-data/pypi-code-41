#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains definitions for asset in Plot Twist
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
import webbrowser

from Qt.QtCore import *
from Qt.QtWidgets import *

import artellapipe
from artellapipe.core import asset as artella_asset

from plottwist.core import defines
from plottwist.pipeline.utils import worker


class PlotTwistAsset(artella_asset.ArtellaAsset, object):
    def __init__(self, project, asset_data):
        super(PlotTwistAsset, self).__init__(project=project, asset_data=asset_data)

    def get_name(self):
        """
        Overrides ArtellaAsset get_name function
        Returns the path of the asset
        :return: str
        """

        return self.data.name

    def get_path(self):
        """
        Overrides ArtellaAsset get_path function
        Returns the path of the asset
        :return: str
        """

        entity_type = self._project.get_entity_type_by_id(self.data.entity_type_id)
        if not entity_type:
            return ''

        entity_type_name = entity_type.name
        entity_path = os.path.join(self._project.get_assets_path(), entity_type_name, self.get_name())

        return entity_path

    def get_category(self):
        """
        Overrides abstract get_thumbnail_icon function
        Returns the category of the asset
        :return: str
        """

        entity_type_id = self.data.entity_type_id
        return self._project.get_entity_type_by_id(entity_type_id)

        return self.data.type

    def get_shading_type(self):
        """
        Implements base ArtellaAsset get_shading_type function
        Returns the asset file type of the shading file for the project
        :return: str
        """

        return defines.PLOTTWIST_SHADING_ASSET_TYPE

    def get_preview_id(self):
        """
        Returns the preview ID of the asset in Kitsu
        :return: str
        """

        return self.data.preview_file_id

    def get_kitsu_assets_url(self):
        """
        Returns Kitsu URL of the assets
        :return: str
        """

        return self._project.get_kitsu_assets_url()

    def open_in_kitsu(self):
        """
        Opens current asset in Kitsu web
        """

        kitsu_asset_url = self.get_kitsu_assets_url()
        asset_url = kitsu_asset_url + '/' + self.data.id
        webbrowser.open(asset_url)

    def _get_file_name(self, asset_name, **kwargs):
        """
        Overrides base ArtellaAsset _get_file_name function
        :param asset_name: str
        :param kwargs: dict
        :return: str
        """

        return self._project.solve_name('asset_file', asset_name)


class PlotTwistAssetWidget(artella_asset.ArtellaAssetWidget, object):

    THUMB_SIZE = (150, 150)

    ThreadPool = QThreadPool()

    def __init__(self, asset, parent=None):

        self._icon_path = None
        self._thumbnail_icon = None
        self._pixmap = None
        self._pixmap_rect = None
        self._pixmap_scaled = None

        super(PlotTwistAssetWidget, self).__init__(asset=asset, parent=parent)

        self._worker = worker.KitsuImageDownloaderWorker()
        self._worker.setAutoDelete(False)
        self._worker.signals.triggered.connect(self._on_thumbnail_from_image)
        self._worker_started = False

        self.asset.get_path()

        self._update_thumbnail_icon()

    def ui(self):
        super(PlotTwistAssetWidget, self).ui()

    def get_thumbnail_path(self):
        """
        Overrides base ArtellaAssetWidget get_thumbnail_path function
        :return: str
        """

        data_path = artellapipe.plottwist.get_data_path()
        thumbnails_cache_folder = os.path.join(data_path, 'asset_thumbs_cache')
        if not os.path.isdir(thumbnails_cache_folder):
            os.makedirs(thumbnails_cache_folder)

        return os.path.join(thumbnails_cache_folder, self.asset.get_name()+'.png')

    def get_thumbnail_icon(self):
        """
        Overrides base ArtellaAssetWidget get_thumbnail_icon function
        :return: QIcon
        """

        return self._thumbnail_icon

    def _create_context_menu(self, context_menu):
        """
        Overrides ArtellaAssetWidget _create_context_menu function
        :param context_menu: QMenu
        """

        super(PlotTwistAssetWidget, self)._create_context_menu(context_menu)

        kitsu_icon = artellapipe.plottwist.resource.icon('kitsu')

        kitsu_action = QAction(kitsu_icon, 'Open in Kitsu', context_menu)

        kitsu_action.triggered.connect(self._on_open_in_kitsu)

        artella_action = context_menu.find_action('Open in Artella')
        if artella_action:
            context_menu.insertAction(artella_action, kitsu_action)
        else:
            context_menu.addAction(kitsu_action)

    def _update_thumbnail_icon(self):
        """
        Internal function that updates the thumbnail icon
        :return:
        """

        thumbnail_path = self.get_thumbnail_path()
        preview_id = self._asset.get_preview_id()
        self._worker_started = True
        self._worker.set_path(thumbnail_path)
        self._worker.set_preview_id(preview_id)
        self.ThreadPool.start(self._worker)
        self._thumbnail_icon = self.DEFAULT_ICON
        self._asset_btn.setIcon(self._thumbnail_icon)

        return self._thumbnail_icon

    def _on_thumbnail_from_image(self, asset_icon):
        """
        Internal callback function that is called when an image object has finished loading
        """

        if asset_icon and not asset_icon.isNull():
            self._thumbnail_icon = asset_icon
            self._asset_btn.setIcon(asset_icon)

    def _on_open_in_kitsu(self):
        """
        Internal callback function that is called when the user presses Open in Kitsu contextual menu action
        """

        self._asset.open_in_kitsu()
