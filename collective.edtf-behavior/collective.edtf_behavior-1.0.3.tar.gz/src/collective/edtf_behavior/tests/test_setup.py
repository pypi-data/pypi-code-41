# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from __future__ import absolute_import
from collective.edtf_behavior.testing import COLLECTIVE_EDTF_BEHAVIOR_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


no_get_installer = False


try:
    from Products.CMFPlone.utils import get_installer
except Exception:
    no_get_installer = True


class TestSetup(unittest.TestCase):
    """Test that collective.edtf_behavior is properly installed."""

    layer = COLLECTIVE_EDTF_BEHAVIOR_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = get_installer(self.portal, self.layer['request'])

    def test_product_installed(self):
        """Test if collective.edtf_behavior is installed."""
        self.assertTrue(self.installer.is_product_installed(
            'collective.edtf_behavior'))

    def test_browserlayer(self):
        """Test that ICollectiveEdtfBehaviorLayer is registered."""
        from collective.edtf_behavior.interfaces import (
            ICollectiveEdtfBehaviorLayer)
        from plone.browserlayer import utils
        self.assertIn(
            ICollectiveEdtfBehaviorLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_EDTF_BEHAVIOR_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = get_installer(self.portal, self.layer['request'])
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstall_product('collective.edtf_behavior')
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if collective.edtf_behavior is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed(
            'collective.edtf_behavior'))

    def test_browserlayer_removed(self):
        """Test that ICollectiveEdtfBehaviorLayer is removed."""
        from collective.edtf_behavior.interfaces import \
            ICollectiveEdtfBehaviorLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            ICollectiveEdtfBehaviorLayer,
            utils.registered_layers())
