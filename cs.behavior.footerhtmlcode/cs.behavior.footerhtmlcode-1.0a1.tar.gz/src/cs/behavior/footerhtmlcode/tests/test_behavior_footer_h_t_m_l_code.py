# -*- coding: utf-8 -*-
from cs.behavior.footerhtmlcode.behaviors.footer_html_code import IFooterHTMLCodeMarker
from cs.behavior.footerhtmlcode.testing import (
    CS_BEHAVIOR_FOOTERHTMLCODE_INTEGRATION_TESTING,
)  # noqa
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.behavior.interfaces import IBehavior
from zope.component import getUtility

import unittest


class FooterHTMLCodeIntegrationTest(unittest.TestCase):

    layer = CS_BEHAVIOR_FOOTERHTMLCODE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_behavior_footer_h_t_m_l_code(self):
        behavior = getUtility(IBehavior, "cs.behavior.footerhtmlcode.footer_html_code")
        self.assertEqual(behavior.marker, IFooterHTMLCodeMarker)
