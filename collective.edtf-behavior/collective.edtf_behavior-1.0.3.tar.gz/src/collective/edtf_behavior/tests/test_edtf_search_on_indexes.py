# -*- coding: utf-8 -*-
from __future__ import absolute_import
from collective.edtf_behavior.behaviors.edtf_date import IEDTFDate
from collective.edtf_behavior.behaviors.edtf_date import IEDTFDateMarker
from collective.edtf_behavior.testing import COLLECTIVE_EDTF_BEHAVIOR_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.schema import SchemaInvalidatedEvent
from zope.component import queryUtility
from zope.event import notify

import datetime
import unittest


class EDTFDateSearchIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_EDTF_BEHAVIOR_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        # enable IEDTFDate behavior on Document
        fti = queryUtility(IDexterityFTI, name='Document')
        behaviors = list(fti.behaviors)
        behaviors.append(IEDTFDate.__identifier__)
        fti.behaviors = tuple(behaviors)
        notify(SchemaInvalidatedEvent('Document'))

        self.document1 = api.content.create(
            container=self.portal,
            type='Document',
            id='doc1',
            edtf_date='1711-11-11',
        )
        self.document2 = api.content.create(
            container=self.portal,
            type='Document',
            id='doc2',
            edtf_date='1920-02-03/1933-04-30',
        )
        self.document3 = api.content.create(
            container=self.portal,
            type='Document',
            id='doc3',
            edtf_date='1920-02-06/1933-04-28',
        )

    def test_edtf_date_behavior_is_enabled(self):

        self.assertTrue(
            IEDTFDateMarker.providedBy(self.document1),
        )

    def test_edtf_date_search_on_latest(self):
        results = api.content.find(
            portal_type='Document',
            date_latest={
                'query': datetime.date(1933, 4, 30),
                'range': 'max',
            },
        )
        self.assertEqual(
            len(results),
            3,
        )

        results = api.content.find(
            portal_type='Document',
            date_latest={
                'query': datetime.date(1933, 4, 29),
                'range': 'max',
            },
        )
        self.assertEqual(
            len(results),
            2,
        )

        results = api.content.find(
            portal_type='Document',
            date_latest={
                'query': datetime.date(1711, 11, 11),
                'range': 'max',
            },
        )
        self.assertEqual(
            len(results),
            1,
        )

        results = api.content.find(
            portal_type='Document',
            date_latest={
                'query': datetime.date(1711, 11, 11),
                'range': 'min',
            },
        )
        self.assertEqual(
            len(results),
            3,
        )

        results = api.content.find(
            portal_type='Document',
            date_latest={
                'query': (
                    datetime.date(1711, 11, 11),
                    datetime.date(1933, 4, 30),
                ),
                'range': 'min:max',
            },
        )
        self.assertEqual(
            len(results),
            3,
        )

    def test_edtf_date_search_on_earliest(self):
        # 1920-02-03 / 1920-02-06 / 1711-11-11
        results = api.content.find(
            portal_type='Document',
            date_earliest={
                'query': datetime.date(1711, 11, 11),
                'range': 'min',
            },
        )
        self.assertEqual(
            len(results),
            3,
        )

        results = api.content.find(
            portal_type='Document',
            date_earliest={
                'query': datetime.date(1920, 2, 3),
                'range': 'min',
            },
        )
        self.assertEqual(
            len(results),
            2,
        )

        results = api.content.find(
            portal_type='Document',
            date_earliest={
                'query': datetime.date(1920, 2, 6),
                'range': 'min',
            },
        )
        self.assertEqual(
            len(results),
            1,
        )

        results = api.content.find(
            portal_type='Document',
            date_earliest={
                'query': datetime.date(1920, 2, 6),
                'range': 'max',
            },
        )
        self.assertEqual(
            len(results),
            3,
        )

        results = api.content.find(
            portal_type='Document',
            date_earliest={
                'query': (
                    datetime.date(1711, 11, 11),
                    datetime.date(1920, 2, 6),
                ),
                'range': 'min:max',
            },
        )
        self.assertEqual(
            len(results),
            3,
        )

    def test_edtf_date_search_on_edtf_date_range(self):
        # 1920-02-03 / 1920-02-06 / 1711-11-11

        results = api.content.find(
            portal_type='Document',
            edtf_start_end_range={
                'start': datetime.date(1711, 11, 11),
                'end': datetime.date(1920, 2, 6),
            },
        )
        self.assertEqual(
            len(results),
            3,
        )

        results = api.content.find(
            portal_type='Document',
            edtf_start_end_range={
                'start': datetime.date(1711, 11, 11),
                'end': datetime.date(1920, 2, 4),
            },
        )
        self.assertEqual(
            len(results),
            2,
        )

        results = api.content.find(
            portal_type='Document',
            edtf_start_end_range={
                'start': datetime.date(1711, 11, 11),
                'end': datetime.date(1933, 4, 29),
            },
        )
        self.assertEqual(
            len(results),
            3,
        )

        results = api.content.find(
            portal_type='Document',
            edtf_start_end_range={
                'start': datetime.date(1933, 4, 1),
                'end': datetime.date(1933, 5, 1),
            },
        )
        self.assertEqual(
            len(results),
            2,
        )

        results = api.content.find(
            portal_type='Document',
            edtf_start_end_range={
                'start': datetime.date(1933, 4, 29),
                'end': datetime.date(1933, 5, 1),
            },
        )
        self.assertEqual(
            len(results),
            1,
        )

    def test_edtf_date_sort_descending(self):
        results = api.content.find(
            portal_type='Document',
            sort_on='date_sort_descending',
            sort_order='descending',
        )
        result_list = [res.getObject().edtf_date for res in results]
        # most recent first
        self.assertEqual(
            result_list,
            ['1920-02-03/1933-04-30', '1920-02-06/1933-04-28', '1711-11-11'],
        )

    def test_edtf_date_sort_ascending(self):
        results = api.content.find(
            portal_type='Document',
            sort_on='date_sort_ascending',
            sort_order='ascending',
        )
        # most recent last
        result_list = [res.getObject().edtf_date for res in results]
        self.assertEqual(
            result_list,
            ['1711-11-11', '1920-02-03/1933-04-30', '1920-02-06/1933-04-28'],
        )
