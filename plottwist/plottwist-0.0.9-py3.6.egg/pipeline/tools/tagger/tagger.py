#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool used to manage metadata for Plot Twist
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import artellapipe
from artellapipe.tools.tagger import tagger


class PlotTwistTagger(tagger.ArtellaTagger, object):
    def __init__(self, project):
        super(PlotTwistTagger, self).__init__(project=project)


def run():
    win = PlotTwistTagger(artellapipe.plottwist)
    win.show()
    return win
