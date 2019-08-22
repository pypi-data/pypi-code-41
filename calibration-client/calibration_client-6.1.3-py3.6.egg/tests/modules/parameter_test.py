"""ParameterTest class"""

import unittest

from calibration_client.calibration_client import CalibrationClient
from .module_base import ModuleBase
from ..common.config_test import *
from ..common.generators import Generators
from ..common.secrets import *
from ...modules.parameter import Parameter

MODULE_NAME = PARAMETER


class ParameterTest(ModuleBase, unittest.TestCase):
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

        __unique_name1 = Generators.generate_unique_name('Parameter01')
        self.par_01 = {
            'name': __unique_name1,
            'unit_id': '-1',
            'flg_available': 'true',
            'flg_logarithmic': 'false',
            'def_lower_deviation_value': '1.0',
            'def_upper_deviation_value': '1.2',
            'description': 'desc 01'
        }

        __unique_name_upd = Generators.generate_unique_name('ParameterUpd01')
        self.par_01_upd = {
            'name': __unique_name_upd,
            'unit_id': '-1',
            'flg_available': 'true',
            'flg_logarithmic': 'false',
            'def_lower_deviation_value': '1.0',
            'def_upper_deviation_value': '1.2',
            'description': 'desc 01'
        }

    def test_create_parameter(self):
        param_01 = Parameter(
            calibration_client=self.cal_client,
            name=self.par_01['name'],
            unit_id=self.par_01['unit_id'],
            flg_available=self.par_01['flg_available'],
            flg_logarithmic=self.par_01['flg_logarithmic'],
            def_lower_deviation_value=self.par_01['def_lower_deviation_value'],
            def_upper_deviation_value=self.par_01['def_upper_deviation_value'],
            description=self.par_01['description'])

        #
        # Create new entry (should succeed)
        #
        result1 = param_01.create()
        self.assert_create_success(MODULE_NAME, result1, self.par_01)

        parameter = result1['data']
        parameter_id = result1['data']['id']
        parameter_name = result1['data']['name']

        #
        # Create duplicated entry (should throw an error)
        #
        param_01_dup = param_01
        result2 = param_01_dup.create()
        expect_app_info = {'name': ['has already been taken']}
        self.assert_create_error(MODULE_NAME, result2, expect_app_info)

        #
        # Get entry by name
        #
        result3 = Parameter.get_by_name(self.cal_client, parameter_name)
        self.assert_find_success(MODULE_NAME, result3, self.par_01)

        #
        # Get entry by ID
        #
        result4 = Parameter.get_by_id(self.cal_client, parameter_id)
        self.assert_find_success(MODULE_NAME, result4, self.par_01)

        #
        # Get entry with non-existent ID (should throw an error)
        #
        parameter_id = -666
        result5 = Parameter.get_by_id(self.cal_client, parameter_id)
        self.assert_find_error(MODULE_NAME, result5, RESOURCE_NOT_FOUND)

        #
        # Put entry information (update some fields should succeed)
        #
        param_01.name = self.par_01_upd['name']
        param_01.flg_available = self.par_01_upd['flg_available']
        param_01.description = self.par_01_upd['description']
        result6 = param_01.update()
        self.assert_update_success(MODULE_NAME, result6, self.par_01_upd)

        #
        # Put entry information (update some fields should throw an error)
        #
        param_01.name = '__THIS_NAME_IS_1_CHARACTERS_LONGER_THAN_THE_ALLOWED_MAX_NUM__'  # noqa
        param_01.flg_available = self.par_01_upd['flg_available']
        param_01.description = self.par_01_upd['description']
        result7 = param_01.update()
        expect_app_info = {'name': ['is too long (maximum is 60 characters)']}
        self.assert_update_error(MODULE_NAME, result7, expect_app_info)

        #
        # Delete entry (should succeed)
        # (test purposes only to keep the DB clean)
        #
        result8 = param_01.delete()
        self.assert_delete_success(MODULE_NAME, result8)

        #
        # Delete entry (should throw an error)
        # (test purposes only to keep the DB clean)
        #
        result9 = param_01.delete()
        self.assert_delete_error(MODULE_NAME, result9, RESOURCE_NOT_FOUND)

    #
    # fields_validation
    #
    def fields_validation(self, receive, expect):
        self.assert_eq_hfield(receive, expect, 'name', STRING)
        self.assert_eq_hfield(receive, expect, 'unit_id', NUMBER)
        self.assert_eq_hfield(receive, expect, 'flg_available', BOOLEAN)
        self.assert_eq_hfield(receive, expect, 'flg_logarithmic', BOOLEAN)
        self.assert_eq_hfield(receive, expect,
                              'def_lower_deviation_value', NUMBER)
        self.assert_eq_hfield(receive, expect,
                              'def_upper_deviation_value', NUMBER)
        self.assert_eq_hfield(receive, expect, 'description', STRING)


if __name__ == '__main__':
    unittest.main()
