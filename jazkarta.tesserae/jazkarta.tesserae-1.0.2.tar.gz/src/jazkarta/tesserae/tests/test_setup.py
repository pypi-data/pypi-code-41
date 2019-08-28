# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from jazkarta.tesserae.testing import JAZKARTA_TESSERAE_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that jazkarta.tesserae is properly installed."""

    layer = JAZKARTA_TESSERAE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if jazkarta.tesserae is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'jazkarta.tesserae'))

    def test_browserlayer(self):
        """Test that IJazkartaTesseraeLayer is registered."""
        from jazkarta.tesserae.interfaces import (
            IJazkartaTesseraeLayer)
        from plone.browserlayer import utils
        self.assertIn(IJazkartaTesseraeLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = JAZKARTA_TESSERAE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['jazkarta.tesserae'])

    def test_product_uninstalled(self):
        """Test if jazkarta.tesserae is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'jazkarta.tesserae'))

    def test_browserlayer_removed(self):
        """Test that IJazkartaTesseraeLayer is removed."""
        from jazkarta.tesserae.interfaces import \
            IJazkartaTesseraeLayer
        from plone.browserlayer import utils
        self.assertNotIn(IJazkartaTesseraeLayer, utils.registered_layers())
