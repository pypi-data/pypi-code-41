#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool that allows to detect errors and trace calls for Plot Twist
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"


import artellapipe
from artellapipe.tools.bugtracker import bugtracker


class PlotTwistBugTracker(bugtracker.ArtellaBugTracker, object):
    def __init__(self, project, tool_name=None, parent=None):
        super(PlotTwistBugTracker, self).__init__(project=project, tool_name=tool_name, parent=parent)

    def ui(self):
        super(PlotTwistBugTracker, self).ui()

        logo_pixmap = artellapipe.plottwist.resource.pixmap(name='bugtracker_logo', extension='png')
        self.set_logo(logo_pixmap)
