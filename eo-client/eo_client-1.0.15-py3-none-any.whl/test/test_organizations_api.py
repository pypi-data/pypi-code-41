# coding: utf-8

"""
    EO Service

    The Enterprise Ontology (EO) aims at establishing a common conceptualization on the Entreprise domain, including organizations, organizational units, people, roles, teams and projects.  # noqa: E501

    OpenAPI spec version: v1
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

import unittest

import eo_client
from eo_client.api.organizations_api import OrganizationsApi  # noqa: E501
from eo_client.rest import ApiException


class TestOrganizationsApi(unittest.TestCase):
    """OrganizationsApi unit test stubs"""

    def setUp(self):
        self.api = eo_client.api.organizations_api.OrganizationsApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_organizations_create(self):
        """Test case for organizations_create

        """
        pass

    def test_organizations_delete(self):
        """Test case for organizations_delete

        """
        pass

    def test_organizations_list(self):
        """Test case for organizations_list

        """
        pass

    def test_organizations_partial_update(self):
        """Test case for organizations_partial_update

        """
        pass

    def test_organizations_read(self):
        """Test case for organizations_read

        """
        pass

    def test_organizations_update(self):
        """Test case for organizations_update

        """
        pass


if __name__ == '__main__':
    unittest.main()
