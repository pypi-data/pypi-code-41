# -*- coding: utf-8 -*-
from __future__ import absolute_import
from collective.edtf_behavior.behaviors.edtf_date import edtf_parseable
from collective.edtf_behavior.behaviors.edtf_date import IEDTFDateMarker
from collective.edtf_behavior.testing import COLLECTIVE_EDTF_BEHAVIOR_INTEGRATION_TESTING  # noqa
from collective.edtf_behavior.upgrades import reload_gs_profile
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.behavior.interfaces import IBehavior
from zope.component import getUtility
from zope.interface import Invalid

import datetime
import unittest


class EDTFDateIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_EDTF_BEHAVIOR_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.document = api.content.create(
            container=self.portal,
            type='Document',
            id='doc1',
        )

    def test_get_behavior_edtf_date(self):
        behavior = getUtility(IBehavior, 'collective.edtf_behavior.edtf_date')
        self.assertEqual(
            behavior.marker,
            IEDTFDateMarker,
        )

    def test_behavior_edtf_date_earliest_latest(self):
        behavior = getUtility(IBehavior, 'collective.edtf_behavior.edtf_date')
        doc_adapted = behavior.factory(self.document)

        doc_adapted.edtf_date = '1711-11-11'
        self.assertEqual(
            doc_adapted.date_earliest,
            datetime.date(1711, 11, 11),
        )
        self.assertEqual(
            doc_adapted.date_latest,
            datetime.date(1711, 11, 11),
        )

        doc_adapted.edtf_date = '1920-02-03/1933-04-30'
        self.assertEqual(
            doc_adapted.date_earliest,
            datetime.date(1920, 2, 3),
        )
        self.assertEqual(
            doc_adapted.date_latest,
            datetime.date(1933, 4, 30),
        )

        doc_adapted.edtf_date = '1811-12-11/1860-03-13'
        self.assertEqual(
            doc_adapted.date_earliest,
            datetime.date(1811, 12, 11),
        )
        self.assertEqual(
            doc_adapted.date_latest,
            datetime.date(1860, 3, 13),
        )

    def test_behavior_edtf_date_sort_asc_desc(self):
        behavior = getUtility(IBehavior, 'collective.edtf_behavior.edtf_date')
        doc_adapted = behavior.factory(self.document)

        doc_adapted.edtf_date = '1711-11-11'
        self.assertEqual(
            doc_adapted.date_sort_ascending,
            datetime.date(1711, 11, 11),
        )
        self.assertEqual(
            doc_adapted.date_sort_descending,
            datetime.date(1711, 11, 11),
        )

        doc_adapted.edtf_date = '1920-03~'
        self.assertEqual(
            doc_adapted.date_sort_ascending,
            datetime.date(1920, 3, 1),
        )
        self.assertEqual(
            doc_adapted.date_sort_descending,
            datetime.date(1920, 3, 31),
        )

        doc_adapted.edtf_date = '1811-12-11/1860-03-13'
        self.assertEqual(
            doc_adapted.date_sort_ascending,
            datetime.date(1811, 12, 11),
        )
        self.assertEqual(
            doc_adapted.date_sort_descending,
            datetime.date(1860, 3, 13),
        )

    def test_behavior_edtf_validator(self):
        with self.assertRaises(Invalid):
            res = edtf_parseable('12.12.2018')
            self.assertFalse(res)

        res = edtf_parseable('2018-12-12')
        self.assertTrue(res)

        res = edtf_parseable('2018-12~')
        self.assertTrue(res)

    def test_upgrades_reload_gs_profile(self):
        reload_gs_profile(self.portal)
