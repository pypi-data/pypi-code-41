# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from uwosh.oie.studyabroadtheme.testing import UWOSH_OIE_STUDYABROADTHEME_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that uwosh.oie.studyabroadtheme is properly installed."""

    layer = UWOSH_OIE_STUDYABROADTHEME_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if uwosh.oie.studyabroadtheme is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'uwosh.oie.studyabroadtheme'))

    def test_browserlayer(self):
        """Test that IUwoshOieStudyabroadthemeLayer is registered."""
        from uwosh.oie.studyabroadtheme.interfaces import (
            IUwoshOieStudyabroadthemeLayer)
        from plone.browserlayer import utils
        self.assertIn(
            IUwoshOieStudyabroadthemeLayer,
            utils.registered_layers(),
        )


class TestUninstall(unittest.TestCase):

    layer = UWOSH_OIE_STUDYABROADTHEME_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['uwosh.oie.studyabroadtheme'])

    def test_product_uninstalled(self):
        """Test if uwosh.oie.studyabroadtheme is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'uwosh.oie.studyabroadtheme'))

    def test_browserlayer_removed(self):
        """Test that IUwoshOieStudyabroadthemeLayer is removed."""
        from uwosh.oie.studyabroadtheme.interfaces import \
            IUwoshOieStudyabroadthemeLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            IUwoshOieStudyabroadthemeLayer,
            utils.registered_layers(),
        )
