"""BaseApiTest Class with helper methods common to all modules tests"""

import unittest

from ..common.config_test import *
from ..common.util import Util


class ApiBase(Util, unittest.TestCase):
    def get_and_validate_create_entry(self, response):
        self.assert_eq_status_code(response.status_code, CREATED)

        resp_content = self.load_response_content(response)
        return resp_content

    def get_and_validate_all_entries_by_name(self, response):
        self.assert_eq_status_code(response.status_code, OK)

        resp_content = self.load_response_content(response)
        return resp_content[0]

    def get_and_validate_entry_by_id(self, response):
        self.assert_eq_status_code(response.status_code, OK)

        resp_content = self.load_response_content(response)
        return resp_content

    def get_and_validate_delete_entry_by_id(self, response):
        self.assert_eq_status_code(response.status_code, NO_CONTENT)

        resp_content = self.load_response_content(response)
        receive = resp_content
        expect = {}

        self.assert_eq_val(receive, expect)

    def get_and_validate_resource_not_found(self, response):
        resp_content = self.load_response_content(response)

        receive = resp_content
        receive_msg = receive['info']
        expect_msg = RESOURCE_NOT_FOUND
        expect = {'info': expect_msg}

        self.assert_eq_status_code(response.status_code, NOT_FOUND)
        self.assertEqual(receive, expect, "Data must not be found")
        self.assert_eq_str(receive_msg, expect_msg)
