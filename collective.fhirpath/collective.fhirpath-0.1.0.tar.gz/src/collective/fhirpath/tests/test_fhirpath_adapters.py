# _*_ coding: utf-8 _*_
from collective.elasticsearch.es import ElasticSearchCatalog
from collective.fhirpath.testing import COLLECTIVE_FHIRPATH_INTEGRATION_TESTING
from fhirpath.enums import FHIR_VERSION
from fhirpath.interfaces import IElasticsearchEngineFactory
from fhirpath.interfaces import IEngine
from fhirpath.interfaces import IFhirSearch
from fhirpath.interfaces import ISearchContext
from fhirpath.interfaces import ISearchContextFactory
from plone import api
from zope.component import queryMultiAdapter

import unittest


__author__ = "Md Nazrul Islam <email2nazrul@gmail.com>"


class AdatptersIntegrationTest(unittest.TestCase):
    """ """

    layer = COLLECTIVE_FHIRPATH_INTEGRATION_TESTING

    def setUp(self):
        """ """
        self.portal = self.layer["portal"]

    def get_es_catalog(self):
        """ """
        return ElasticSearchCatalog(api.portal.get_tool("portal_catalog"))

    def test_engine_creation(self):
        """ """
        factory = queryMultiAdapter(
            (self.get_es_catalog(),), IElasticsearchEngineFactory
        )
        self.assertIsNotNone(factory)
        engine = factory(fhir_version=FHIR_VERSION.STU3)
        self.assertTrue(IEngine.providedBy(engine))

    def test_search_context_creation(self):
        """ """
        engine = queryMultiAdapter(
            (self.get_es_catalog(),), IElasticsearchEngineFactory
        )(fhir_version=FHIR_VERSION.STU3)

        factory = queryMultiAdapter(
            (engine,), ISearchContextFactory
        )
        self.assertIsNotNone(factory)

        context = factory("Organization")
        self.assertTrue(ISearchContext.providedBy(context))

    def test_search_factory_creation(self):
        """ """
        engine = queryMultiAdapter(
            (self.get_es_catalog(),), IElasticsearchEngineFactory
        )(fhir_version=FHIR_VERSION.STU3)

        context = queryMultiAdapter(
            (engine,), ISearchContextFactory
        )("Organization")

        factory = queryMultiAdapter(
            (context,), IFhirSearch
        )
        self.assertIsNotNone(factory)
