"""CalibrationTest class"""

import unittest

from calibration_client.calibration_client import CalibrationClient
from .module_base import ModuleBase
from ..common.config_test import *
from ..common.generators import Generators
from ..common.secrets import *
from ...modules.calibration import Calibration

MODULE_NAME = CALIBRATION


class CalibrationTest(ModuleBase, unittest.TestCase):
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

        __unique_name1 = Generators.generate_unique_name('Calibration01')
        self.cal_01 = {
            'name': __unique_name1,
            'unit_id': '-1',
            'max_value': '10.0',
            'min_value': '1.0',
            'allowed_deviation': '0.1',
            'description': 'desc 01'
        }

        __unique_name_upd = Generators.generate_unique_name('CalibrationUpd01')
        self.cal_01_upd = {
            'name': __unique_name_upd,
            'unit_id': '-1',
            'max_value': '12.0',
            'min_value': '3.0',
            'allowed_deviation': '0.5',
            'description': 'desc 01 updated!'
        }

    def test_create_calibration(self):
        cal_01 = Calibration(
            calibration_client=self.cal_client,
            name=self.cal_01['name'],
            unit_id=self.cal_01['unit_id'],
            max_value=self.cal_01['max_value'],
            min_value=self.cal_01['min_value'],
            allowed_deviation=self.cal_01['allowed_deviation'],
            description=self.cal_01['description']
        )

        #
        # Create new entry (should succeed)
        #
        result1 = cal_01.create()
        self.assert_create_success(MODULE_NAME, result1, self.cal_01)

        calibration = result1['data']
        calibration_id = result1['data']['id']
        calibration_name = result1['data']['name']

        #
        # Create duplicated entry (should throw an error)
        #
        cal_01_dup = cal_01
        result2 = cal_01_dup.create()
        expect_app_info = {'name': ['has already been taken'],
                           'unit': ['has already been taken']}
        self.assert_create_error(MODULE_NAME, result2, expect_app_info)

        #
        # Get entry by name
        #
        result3 = Calibration.get_by_name(self.cal_client, calibration_name)
        self.assert_find_success(MODULE_NAME, result3, self.cal_01)

        #
        # Get entry by ID
        #
        result4 = Calibration.get_by_id(self.cal_client, calibration_id)
        self.assert_find_success(MODULE_NAME, result4, self.cal_01)

        #
        # Get entry with non-existent ID (should throw an error)
        #
        calibration_id = -666
        result5 = Calibration.get_by_id(self.cal_client, calibration_id)
        self.assert_find_error(MODULE_NAME, result5, RESOURCE_NOT_FOUND)

        #
        # Put entry information (update some fields should succeed)
        #
        cal_01.name = self.cal_01_upd['name']
        cal_01.max_value = self.cal_01_upd['max_value']
        cal_01.min_value = self.cal_01_upd['min_value']
        cal_01.allowed_deviation = self.cal_01_upd['allowed_deviation']
        cal_01.description = self.cal_01_upd['description']
        result6 = cal_01.update()
        self.assert_update_success(MODULE_NAME, result6, self.cal_01_upd)

        #
        # Put entry information (update some fields should throw an error)
        #
        cal_01.name = '__THIS_NAME_IS_1_CHARACTERS_LONGER_THAN_THE_ALLOWED_MAX_NUM__'  # noqa
        cal_01.max_value = self.cal_01_upd['max_value']
        cal_01.min_value = self.cal_01_upd['min_value']
        cal_01.allowed_deviation = self.cal_01_upd['allowed_deviation']
        cal_01.description = self.cal_01_upd['description']
        result7 = cal_01.update()
        expect_app_info = {'name': ['is too long (maximum is 60 characters)']}
        self.assert_update_error(MODULE_NAME, result7, expect_app_info)

        #
        # Delete entry (should succeed)
        # (test purposes only to keep the DB clean)
        #
        result8 = cal_01.delete()
        self.assert_delete_success(MODULE_NAME, result8)

        #
        # Delete entry (should throw an error)
        # (test purposes only to keep the DB clean)
        #
        result9 = cal_01.delete()
        self.assert_delete_error(MODULE_NAME, result9, RESOURCE_NOT_FOUND)

    #
    # fields_validation
    #
    def fields_validation(self, receive, expect):
        self.assert_eq_hfield(receive, expect, 'name', STRING)
        self.assert_eq_hfield(receive, expect, 'unit_id', NUMBER)
        self.assert_eq_hfield(receive, expect, 'max_value', NUMBER)
        self.assert_eq_hfield(receive, expect, 'min_value', NUMBER)
        self.assert_eq_hfield(receive, expect, 'allowed_deviation', NUMBER)
        self.assert_eq_hfield(receive, expect, 'description', STRING)


if __name__ == '__main__':
    unittest.main()
