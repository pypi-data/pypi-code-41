"""CalibrationApiTest class"""

import unittest

from .api_base import ApiBase
from ..common.config_test import *
from ..common.generators import Generators
from ..common.secrets import *
from ...calibration_client_api import CalibrationClientApi


class CalibrationApiTest(ApiBase, unittest.TestCase):
    cal_client_api = CalibrationClientApi(
        client_id=CLIENT_OAUTH2_INFO['CLIENT_ID'],
        client_secret=CLIENT_OAUTH2_INFO['CLIENT_SECRET'],
        token_url=CLIENT_OAUTH2_INFO['TOKEN_URL'],
        refresh_url=CLIENT_OAUTH2_INFO['REFRESH_URL'],
        auth_url=CLIENT_OAUTH2_INFO['AUTH_URL'],
        scope=CLIENT_OAUTH2_INFO['SCOPE'],
        user_email=CLIENT_OAUTH2_INFO['EMAIL'],
        base_api_url=BASE_API_URL)

    def test_create_calibration_api(self):
        __unique_name = Generators.generate_unique_name('CalibrationApi')
        calibration = {
            'calibration': {
                'name': __unique_name,
                'unit_id': '-1',
                'max_value': '10.0',
                'min_value': '1.0',
                'allowed_deviation': '0.1',
                'description': 'desc 01'
            }
        }

        expect = calibration['calibration']

        #
        # Create new entry (should succeed)
        #
        received = self.__create_entry_api(calibration, expect)

        calibration_id = received['id']
        calibration_name = received['name']

        #
        # Create duplicated entry (should throw an error)
        #
        self.__create_error_entry_uk_api(calibration)

        #
        # Get entry by name
        #
        self.__get_all_entries_by_name_api(calibration_name, expect)

        #
        # Get entry by ID
        #
        self.__get_entry_by_id_api(calibration_id, expect)

        #
        # Put entry information (update some fields should succeed)
        #
        self.__update_entry_api(calibration_id, expect)

        #
        # Delete entry (should succeed)
        # (test purposes only to keep the DB clean)
        #
        self.__delete_entry_by_id_api(calibration_id)

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

    #
    # Internal private APIs methods
    #
    def __create_entry_api(self, entry_info, expect):
        response = self.cal_client_api.create_calibration_api(entry_info)
        receive = self.get_and_validate_create_entry(response)
        self.fields_validation(receive, expect)
        return receive

    def __create_error_entry_uk_api(self, entry_info):
        response = self.cal_client_api.create_calibration_api(entry_info)
        resp_content = self.load_response_content(response)

        receive = resp_content
        expect = {'info': {'name': ['has already been taken'],
                           'unit': ['has already been taken']}}

        self.assertEqual(receive, expect, "Expected result not received")
        self.assert_eq_status_code(response.status_code, UNPROCESSABLE_ENTITY)

        # 'has already been taken'
        receive_msg_name = receive['info']['name'][0]
        expect_msg_name = expect['info']['name'][0]
        self.assert_eq_str(receive_msg_name, expect_msg_name)

        # 'has already been taken'
        receive_msg_unit = receive['info']['unit'][0]
        expect_msg_unit = expect['info']['unit'][0]
        self.assert_eq_str(receive_msg_unit, expect_msg_unit)

    def __update_entry_api(self, entry_id, expect):
        unique_name = Generators.generate_unique_name('CalibrationApiUpd')
        calibration_upd = {
            'calibration': {
                'name': unique_name,
                # 'unit_id': '-1',
                'max_value': '12.0',
                'min_value': '3.0',
                'allowed_deviation': '0.5',
                'description': 'desc 01 updated!'
            }
        }

        resp = self.cal_client_api.update_calibration_api(entry_id,
                                                          calibration_upd)
        resp_content = self.load_response_content(resp)

        receive = resp_content

        # Add parameters not send to the update API
        calibration_upd['calibration']['unit_id'] = '-1'
        expect_upd = calibration_upd['calibration']

        self.fields_validation(receive, expect_upd)
        self.assert_eq_status_code(resp.status_code, OK)

        field = 'name'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'max_value'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'min_value'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'allowed_deviation'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'description'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)

    def __get_all_entries_by_name_api(self, name, expect):
        response = self.cal_client_api.get_all_calibrations_by_name_api(name)
        receive = self.get_and_validate_all_entries_by_name(response)
        self.fields_validation(receive, expect)

    def __get_entry_by_id_api(self, entry_id, expect):
        response = self.cal_client_api.get_calibration_by_id_api(entry_id)
        receive = self.get_and_validate_entry_by_id(response)
        self.fields_validation(receive, expect)

    def __delete_entry_by_id_api(self, entry_id):
        response = self.cal_client_api.delete_calibration_api(entry_id)
        self.get_and_validate_delete_entry_by_id(response)


if __name__ == '__main__':
    unittest.main()
