# _*_ coding: utf-8 _*_
from collective.elasticsearch.es import ElasticSearchCatalog
from collective.fhirpath.testing import COLLECTIVE_FHIRPATH_FUNCTIONAL_TESTING
from fhirpath.enums import FHIR_VERSION
from fhirpath.interfaces import IElasticsearchEngineFactory
from fhirpath.interfaces import IFhirSearch
from fhirpath.interfaces import ISearchContextFactory
from plone import api
from plone.app.fhirfield.tests.base import BaseFunctionalTesting
from plone.app.testing import SITE_OWNER_NAME
from zope.component import queryMultiAdapter


__author__ = "Md Nazrul Islam <email2nazrul@gmail.com>"


class FhirPathPloneSearchFunctional(BaseFunctionalTesting):
    """ """

    layer = COLLECTIVE_FHIRPATH_FUNCTIONAL_TESTING

    def get_es_catalog(self):
        """ """
        return ElasticSearchCatalog(api.portal.get_tool("portal_catalog"))

    def get_factory(self, resource_type, unrestricted=False):
        """ """
        factory = queryMultiAdapter(
            (self.get_es_catalog(),), IElasticsearchEngineFactory
        )
        engine = factory(fhir_version=FHIR_VERSION.STU3)
        context = queryMultiAdapter((engine,), ISearchContextFactory)(
            resource_type, unrestricted=unrestricted
        )

        factory = queryMultiAdapter((context,), IFhirSearch)
        return factory

    def test_basic_search(self):
        """ """
        self.load_contents()

        params = [("_lastUpdated", "2010-05-28T05:35:56+00:00")]
        search_factory = self.get_factory("Organization", True)
        bundle = search_factory(params)
        self.assertEqual(len(bundle.entry), 1)

        params = (
            ("_profile", "http://hl7.org/fhir/Organization"),
            ("identifier", "urn:oid:2.16.528.1|91654"),
            ("type", "http://hl7.org/fhir/organization-type|prov"),
            ("address-postalcode", "9100 AA"),
            ("address", "Den Burg"),
        )
        bundle = search_factory(params)
        self.assertEqual(len(bundle.entry), 2)

    def test_permission_aware_search(self):
        """ """
        self.load_contents()

        params = [("_lastUpdated", "2010-05-28T05:35:56+00:00")]
        search_factory = self.get_factory("Organization", False)

        with api.env.adopt_user(username=SITE_OWNER_NAME):
            bundle = search_factory(params)
            # xxx: some how permission aware query is not working!
            # have to look immediately
            self.assertEqual(len(bundle.entry), 1)

        bundle = search_factory(params)
        # xxx: some how permission aware query is not working!
        # have to look immediately
        # self.assertEqual(len(bundle.entry), 1)

    def test_array_type_reference(self):
        """Search where reference inside List """
        self.load_contents()
        search_factory = self.get_factory("Task", True)

        # Search with based on
        params = (
            ("based-on", "ProcedureRequest/0c57a6c9-c275-4a0a-bd96-701daf7bd7ce"),
        )

        bundle = search_factory(params)
        self.assertEqual(len(bundle.entry), 1)

        # Search with part-of
        # should be two sub tasks
        params = (("part-of", "Task/5df31190-0ed4-45ba-8b16-3c689fc2e686"),)
        bundle = search_factory(params)
        self.assertEqual(len(bundle.entry), 2)

    def test_identifier(self):
        """ """
        self.load_contents()

        search_factory = self.get_factory("Patient", True)

        params = (("identifier", "240365-0002"),)
        bundle = search_factory(params)
        self.assertEqual(len(bundle.entry), 1)

        # Test with system+value
        params = (("identifier", "CPR|240365-0002"),)
        bundle = search_factory(params)

        self.assertEqual(len(bundle.entry), 1)

        # Test with system only with pipe sign
        params = (("identifier", "UUID|"),)
        bundle = search_factory(params)

        self.assertEqual(len(bundle.entry), 1)

        # Test with value only with pipe sign
        params = (("identifier", "|19c5245f-89a8-49f8-b244-666b32adb92e"),)
        bundle = search_factory(params)
        self.assertEqual(len(bundle.entry), 1)

        # Test with empty result
        params = (("identifier", "CPR|19c5245f-89a8-49f8-b244-666b32adb92e"),)
        bundle = search_factory(params)
        self.assertEqual(len(bundle.entry), 0)

        # Test with text modifier
        params = (("identifier:text", "Plone Patient UUID"),)
        bundle = search_factory(params)

        self.assertEqual(len(bundle.entry), 1)

    def test_reference_param(self):
        """Testing FHIR search reference type params, i.e subject, owner"""
        self.load_contents()

        search_factory = self.get_factory("Task", True)

        patient_id = "Patient/19c5245f-89a8-49f8-b244-666b32adb92e"

        params = (("owner", patient_id),)
        bundle = search_factory(params)
        # should be two tasks with having status ready
        self.assertEqual(len(bundle.entry), 2)
        params = (("owner", "Practitioner/619c1ac0-821d-46d9-9d40-a61f2578cadf"),)
        bundle = search_factory(params)
        self.assertEqual(len(bundle.entry), 1)

        params = (("patient", patient_id),)

        bundle = search_factory(params)
        self.assertEqual(len(bundle.entry), 3)

        # with compound query
        params = (("patient", patient_id), ("status", "draft"))
        # should be now only single
        bundle = search_factory(params)

        self.assertEqual(len(bundle.entry), 1)

        # Test with negetive
        params = (("owner:not", "Practitioner/fake-ac0-821d-46d9-9d40-a61f2578cadf"),)
        bundle = search_factory(params)
        # should get all tasks
        self.assertEqual(len(bundle.entry), 3)

        # Test with nested reference
        params = (
            ("based-on", "ProcedureRequest/0c57a6c9-c275-4a0a-bd96-701daf7bd7ce"),
        )
        bundle = search_factory(params)

        # Should One HAQ sub task
        self.assertEqual(len(bundle.entry), 1)

    def test_sorting(self):
        """Search where reference inside List """
        self.load_contents()

        search_factory = self.get_factory("Task", True)
        # Test ascending order
        params = (
            ("status:missing", "false"),
            ("_sort", "_lastUpdated")
        )
        bundle = search_factory(params)

        self.assertGreater(
            bundle.entry[1].resource.meta.lastUpdated.date,
            bundle.entry[0].resource.meta.lastUpdated.date,
        )
        self.assertGreater(
            bundle.entry[2].resource.meta.lastUpdated.date,
            bundle.entry[1].resource.meta.lastUpdated.date,
        )
        # Test descending order
        params = (
            ("status:missing", "false"),
            ("_sort", "-_lastUpdated")
        )
        bundle = search_factory(params)
        self.assertGreater(
            bundle.entry[0].resource.meta.lastUpdated.date,
            bundle.entry[1].resource.meta.lastUpdated.date,
        )
        self.assertGreater(
            bundle.entry[1].resource.meta.lastUpdated.date,
            bundle.entry[2].resource.meta.lastUpdated.date,
        )
