"""PhysicalDeviceApiTest class"""

import unittest

from .api_base import ApiBase
from ..common.config_test import *
from ..common.generators import Generators
from ..common.secrets import *
from ...calibration_client_api import CalibrationClientApi


class PhysicalDeviceApiTest(ApiBase, unittest.TestCase):
    cal_client_api = CalibrationClientApi(
        client_id=CLIENT_OAUTH2_INFO['CLIENT_ID'],
        client_secret=CLIENT_OAUTH2_INFO['CLIENT_SECRET'],
        token_url=CLIENT_OAUTH2_INFO['TOKEN_URL'],
        refresh_url=CLIENT_OAUTH2_INFO['REFRESH_URL'],
        auth_url=CLIENT_OAUTH2_INFO['AUTH_URL'],
        scope=CLIENT_OAUTH2_INFO['SCOPE'],
        user_email=CLIENT_OAUTH2_INFO['EMAIL'],
        base_api_url=BASE_API_URL)

    def test_create_physical_device_api(self):
        __unique_name = Generators.generate_unique_name('PhysicalDeviceApi')
        physical_device = {
            PHYSICAL_DEVICE: {
                'name': __unique_name,
                'device_type_id': '-1',
                'flg_available': 'true',
                'parent_id': None,
                'description': 'desc 01'
            }
        }

        expect = physical_device[PHYSICAL_DEVICE]

        #
        # Create new entry (should succeed)
        #
        received = self.__create_entry_api(physical_device, expect)

        physical_dev_id = received['id']
        physical_dev_name = received['name']

        #
        # Create duplicated entry (should throw an error)
        #
        self.__create_error_entry_uk_api(physical_device)

        #
        # Get entry by name
        #
        self.__get_all_entries_by_name_api(physical_dev_name, expect)

        #
        # Get entry by ID
        #
        self.__get_entry_by_id_api(physical_dev_id, expect)

        #
        # Put entry information (update some fields should succeed)
        #
        self.__update_entry_api(physical_dev_id, expect)

        #
        # Delete entry (should succeed)
        # (test purposes only to keep the DB clean)
        #
        self.__delete_entry_by_id_api(physical_dev_id)

    #
    # fields_validation
    #
    def fields_validation(self, receive, expect):
        self.assert_eq_hfield(receive, expect, 'name', STRING)
        self.assert_eq_hfield(receive, expect, 'device_type_id', NUMBER)
        self.assert_eq_hfield(receive, expect, 'flg_available', BOOLEAN)
        self.assert_eq_hfield(receive, expect, 'parent_id', NUMBER)
        self.assert_eq_hfield(receive, expect, 'description', STRING)

    #
    # Internal private APIs methods
    #
    def __create_entry_api(self, entry_info, expect):
        response = self.cal_client_api.create_physical_device_api(entry_info)
        receive = self.get_and_validate_create_entry(response)
        self.fields_validation(receive, expect)
        return receive

    def __create_error_entry_uk_api(self, entry_info):
        response = self.cal_client_api.create_physical_device_api(entry_info)
        resp_content = self.load_response_content(response)

        receive = resp_content
        expect = {'info': {'name': ['has already been taken']}}

        self.assertEqual(receive, expect, "Expected result not received")
        self.assert_eq_status_code(response.status_code, UNPROCESSABLE_ENTITY)

        # 'has already been taken'
        receive_msg = receive['info']['name'][0]
        expect_msg = expect['info']['name'][0]
        self.assert_eq_str(receive_msg, expect_msg)

    def __update_entry_api(self, entry_id, expect):
        unique_name_upd = Generators.generate_unique_name('PhysicalDevApiUpd')
        physical_dev_upd = {
            PHYSICAL_DEVICE: {
                'name': unique_name_upd,
                # 'device_type_id': '-1',
                'flg_available': 'false',
                # 'parent_id': None,
                'description': 'desc 01 updated!!!'
            }
        }

        resp = self.cal_client_api.update_physical_device_api(entry_id,
                                                              physical_dev_upd)
        resp_content = self.load_response_content(resp)

        receive = resp_content

        # Add parameters not send to the update API
        physical_dev_upd[PHYSICAL_DEVICE]['device_type_id'] = '-1'
        physical_dev_upd[PHYSICAL_DEVICE]['parent_id'] = None
        expect_upd = physical_dev_upd[PHYSICAL_DEVICE]

        self.fields_validation(receive, expect_upd)
        self.assert_eq_status_code(resp.status_code, OK)

        field = 'name'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'flg_available'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'description'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)

    def __get_all_entries_by_name_api(self, name, expect):
        response = self.cal_client_api.get_all_physical_devices_by_name_api(
            name)
        receive = self.get_and_validate_all_entries_by_name(response)
        self.fields_validation(receive, expect)

    def __get_entry_by_id_api(self, entry_id, expect):
        response = self.cal_client_api.get_physical_device_by_id_api(entry_id)
        receive = self.get_and_validate_entry_by_id(response)
        self.fields_validation(receive, expect)

    def __delete_entry_by_id_api(self, entry_id):
        response = self.cal_client_api.delete_physical_device_api(entry_id)
        self.get_and_validate_delete_entry_by_id(response)


if __name__ == '__main__':
    unittest.main()
