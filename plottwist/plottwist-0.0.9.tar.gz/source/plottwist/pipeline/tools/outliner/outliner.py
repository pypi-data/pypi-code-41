#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool that allow to manage scene assets for Plot Twist
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import tpDccLib as tp

import artellapipe
from artellapipe.gui import window
from artellapipe.tools.outliner import outliner


class PlotTwistOutlinerWidget(outliner.ArtellaOutlinerWidget, object):

    title = 'Plot Twist - Outliner'

    def __init__(self, project, parent=None):
        super(PlotTwistOutlinerWidget, self).__init__(project=project, parent=parent)


class PlotTwistOutliner(outliner.ArtellaOutliner, object):
    def __init__(self, project, parent=None):
        super(PlotTwistOutliner, self).__init__(project=project, parent=parent)


def run():
    if tp.is_maya():
        win = window.dock_window(project=artellapipe.plottwist, window_class=PlotTwistOutlinerWidget)
        return win
    else:
        win = PlotTwistOutliner(project=artellapipe.plottwist)
        win.show()
        return win
