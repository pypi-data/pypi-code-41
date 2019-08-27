#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains widget implementation for asset viewer for Plot Twist
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import artellapipe
from artellapipe.core import defines, assetsviewer

from plottwist.core import asset


class PlotTwistAssetsViewer(assetsviewer.AssetsViewer, object):

    ASSET_WIDGET_CLASS = asset.PlotTwistAssetWidget

    def __init__(self, project, column_count=3, parent=None):
        super(PlotTwistAssetsViewer, self).__init__(project=project, column_count=column_count, parent=parent)

    def change_category(self, category=None):
        """
        Overrides base AssetsViewer change_category function
        :param category: str
        """

        if not category:
            category = defines.ARTELLA_ALL_CATEGORIES_NAME

        categories_dict = dict()
        asset_types = self._project.update_types_from_kitsu(force=False)
        for asset_type in asset_types:
            categories_dict[asset_type] = asset_type

        if category != defines.ARTELLA_ALL_CATEGORIES_NAME and category not in categories_dict.keys():
            artellapipe.logger.warning('Asset Type {} is not a valid asset type for project {}'.format(category, self._project.name.title()))
            category = defines.ARTELLA_ALL_CATEGORIES_NAME
        else:
            if category != defines.ARTELLA_ALL_CATEGORIES_NAME:
                category = categories_dict[category]

        self.clear()

        new_assets = list()
        for new_asset in reversed(self._assets):
            if category == defines.ARTELLA_ALL_CATEGORIES_NAME:
                new_asset.setVisible(True)
                new_assets.insert(0, new_asset)
            else:
                if new_asset.asset.get_category().name == category:
                    new_asset.setVisible(True)
                    new_assets.insert(0, new_asset)
                else:
                    new_asset.setVisible(False)
                    new_assets.append(new_asset)

        for new_asset in new_assets:
            self._add_widget(new_asset)

