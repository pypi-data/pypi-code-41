# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from __future__ import absolute_import
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ICollectiveEdtfBehaviorLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""
