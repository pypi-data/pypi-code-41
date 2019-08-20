# coding: utf-8

"""
    IBM Key Protect API

    IBM Key Protect helps you provision encrypted keys for apps across IBM Cloud. As you manage the lifecycle of your keys, you can benefit from knowing that your keys are secured by cloud-based FIPS 140-2 Level 2 hardware security modules (HSMs) that protect against theft of information. You can use the Key Protect API to store, generate, and retrieve your key material. Keys within the service can protect any type of data in your symmetric key based encryption solution.  # noqa: E501

    The version of the OpenAPI document: 2.0.0
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest

import keyprotect
from keyprotect.models.policy import Policy  # noqa: E501
from keyprotect.rest import ApiException


class TestPolicy(unittest.TestCase):
    """Policy unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testPolicy(self):
        """Test Policy"""
        # FIXME: construct object with mandatory attributes with example values
        # model = keyprotect.models.policy.Policy()  # noqa: E501
        pass


if __name__ == '__main__':
    unittest.main()
