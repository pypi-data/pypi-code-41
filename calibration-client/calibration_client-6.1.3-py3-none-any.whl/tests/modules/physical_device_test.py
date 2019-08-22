"""PhysicalDeviceTest class"""

import unittest

from calibration_client.calibration_client import CalibrationClient
from .module_base import ModuleBase
from ..common.config_test import *
from ..common.generators import Generators
from ..common.secrets import *
from ...modules.physical_device import PhysicalDevice

MODULE_NAME = PHYSICAL_DEVICE


class PhysicalDeviceTest(ModuleBase, unittest.TestCase):
    def setUp(self):
        self.cal_client = CalibrationClient(
            client_id=CLIENT_OAUTH2_INFO['CLIENT_ID'],
            client_secret=CLIENT_OAUTH2_INFO['CLIENT_SECRET'],
            token_url=CLIENT_OAUTH2_INFO['TOKEN_URL'],
            refresh_url=CLIENT_OAUTH2_INFO['REFRESH_URL'],
            auth_url=CLIENT_OAUTH2_INFO['AUTH_URL'],
            scope=CLIENT_OAUTH2_INFO['SCOPE'],
            user_email=CLIENT_OAUTH2_INFO['EMAIL'],
            base_api_url=BASE_API_URL
        )

        __unique_name1 = Generators.generate_unique_name('PhysicalDev01')
        self.pd_01 = {
            'name': __unique_name1,
            'device_type_id': '-1',
            'flg_available': 'true',
            'parent_id': None,
            'description': 'desc 01'
        }

        __unique_name_upd = Generators.generate_unique_name('PhysicalDevUpd01')
        self.pd_01_upd = {
            'name': __unique_name_upd,
            'device_type_id': '-1',
            'flg_available': 'false',
            'parent_id': None,
            'description': 'desc 01 Updated!!!'
        }

    def test_create_physical_device(self):
        pd_01 = PhysicalDevice(calibration_client=self.cal_client,
                               name=self.pd_01['name'],
                               device_type_id=self.pd_01['device_type_id'],
                               flg_available=self.pd_01['flg_available'],
                               parent_id=self.pd_01['parent_id'],
                               description=self.pd_01['description'])

        #
        # Create new entry (should succeed)
        #
        result1 = pd_01.create()
        self.assert_create_success(MODULE_NAME, result1, self.pd_01)

        physical_device = result1['data']
        physical_dev_id = result1['data']['id']
        physical_dev_name = result1['data']['name']

        #
        # Create duplicated entry (should throw an error)
        #
        pd_01_dup = pd_01
        result2 = pd_01_dup.create()
        expect_app_info = {'name': ['has already been taken']}
        self.assert_create_error(MODULE_NAME, result2, expect_app_info)

        #
        # Get entry by name
        #
        res3 = PhysicalDevice.get_by_name(self.cal_client, physical_dev_name)
        self.assert_find_success(MODULE_NAME, res3, self.pd_01)

        #
        # Get entry by ID
        #
        result4 = PhysicalDevice.get_by_id(self.cal_client, physical_dev_id)
        self.assert_find_success(MODULE_NAME, result4, self.pd_01)

        #
        # Get entry with non-existent ID (should throw an error)
        #
        physical_device_id = -666
        result5 = PhysicalDevice.get_by_id(self.cal_client, physical_device_id)
        self.assert_find_error(MODULE_NAME, result5, RESOURCE_NOT_FOUND)

        #
        # Put entry information (update some fields should succeed)
        #
        pd_01.name = self.pd_01_upd['name']
        pd_01.flg_available = self.pd_01_upd['flg_available']
        pd_01.description = self.pd_01_upd['description']
        result6 = pd_01.update()
        self.assert_update_success(MODULE_NAME, result6, self.pd_01_upd)

        #
        # Put entry information (update some fields should throw an error)
        #
        pd_01.name = '__THIS_NAME_IS_1_CHARACTERS_LONGER_THAN_THE_ALLOWED_MAX_NUM__'  # noqa
        pd_01.flg_available = self.pd_01_upd['flg_available']
        pd_01.description = self.pd_01_upd['description']
        result7 = pd_01.update()
        expect_app_info = {'name': ['is too long (maximum is 60 characters)']}
        self.assert_update_error(MODULE_NAME, result7, expect_app_info)

        #
        # Delete entry (should succeed)
        # (test purposes only to keep the DB clean)
        #
        result8 = pd_01.delete()
        self.assert_delete_success(MODULE_NAME, result8)

        #
        # Delete entry (should throw an error)
        # (test purposes only to keep the DB clean)
        #
        result9 = pd_01.delete()
        self.assert_delete_error(MODULE_NAME, result9, RESOURCE_NOT_FOUND)

    #
    # fields_validation
    #
    def fields_validation(self, receive, expect):
        self.assert_eq_hfield(receive, expect, 'name', STRING)
        self.assert_eq_hfield(receive, expect, 'device_type_id', NUMBER)
        self.assert_eq_hfield(receive, expect, 'flg_available', BOOLEAN)
        self.assert_eq_hfield(receive, expect, 'parent_id', NUMBER)
        self.assert_eq_hfield(receive, expect, 'description', STRING)


if __name__ == '__main__':
    unittest.main()
