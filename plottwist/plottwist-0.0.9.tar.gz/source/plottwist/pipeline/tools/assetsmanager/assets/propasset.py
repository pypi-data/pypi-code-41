#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains definitions for prop assets in Plot Twist
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import artellapipe

from plottwist.core import defines, asset


class PlotTwistPropAsset(asset.PlotTwistAsset, object):

    ASSET_TYPE = defines.PLOTTWIST_PROP_ASSETS
    ASSET_FILES = {
        defines.PLOTTWIST_TEXTURES_ASSET_TYPE: artellapipe.resource.icon(defines.PLOTTWIST_TEXTURES_ASSET_TYPE),
        defines.PLOTTWIST_MODEL_ASSET_TYPE: artellapipe.resource.icon(defines.PLOTTWIST_MODEL_ASSET_TYPE),
        defines.PLOTTWIST_SHADING_ASSET_TYPE: artellapipe.resource.icon(defines.PLOTTWIST_SHADING_ASSET_TYPE),
        defines.PLOTTWIST_RIG_ASSET_TYPE: artellapipe.resource.icon(defines.PLOTTWIST_RIG_ASSET_TYPE)
    }

    def __init__(self, project, asset_data):
        super(PlotTwistPropAsset, self).__init__(project=project, asset_data=asset_data)
