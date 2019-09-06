# -*- coding: utf-8 -*-
from cs.behavior.footerhtmlcode.interfaces import ICsBehaviorFooterhtmlcodeLayer
from cs.behavior.footerhtmlcode.testing import (
    CS_BEHAVIOR_FOOTERHTMLCODE_FUNCTIONAL_TESTING,
)
from cs.behavior.footerhtmlcode.testing import (
    CS_BEHAVIOR_FOOTERHTMLCODE_INTEGRATION_TESTING,
)
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.Five.browser import BrowserView
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.viewlet.interfaces import IViewletManager

import unittest


class ViewletIntegrationTest(unittest.TestCase):

    layer = CS_BEHAVIOR_FOOTERHTMLCODE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.app = self.layer["app"]
        self.request = self.app.REQUEST
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        api.content.create(self.portal, "Document", "other-document")
        api.content.create(self.portal, "News Item", "newsitem")

    def test_custom_html_code_viewlet_is_registered(self):
        view = BrowserView(self.portal["other-document"], self.request)
        manager_name = "plone.portalfooter"
        alsoProvides(self.request, ICsBehaviorFooterhtmlcodeLayer)
        manager = queryMultiAdapter(
            (self.portal["other-document"], self.request, view),
            IViewletManager,
            manager_name,
            default=None,
        )
        self.assertIsNotNone(manager)
        manager.update()
        my_viewlet = [
            v for v in manager.viewlets if v.__name__ == "custom-html-code-viewlet"
        ]  # NOQA: E501
        self.assertEqual(len(my_viewlet), 1)


class ViewletFunctionalTest(unittest.TestCase):

    layer = CS_BEHAVIOR_FOOTERHTMLCODE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
