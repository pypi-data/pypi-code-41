"""CalibrationConstantApiTest class"""

import unittest

from .api_base import ApiBase
from ..common.config_test import *
from ..common.generators import Generators
from ..common.secrets import *
from ...calibration_client_api import CalibrationClientApi


class CalibrationConstantApiTest(ApiBase, unittest.TestCase):
    cal_client_api = CalibrationClientApi(
        client_id=CLIENT_OAUTH2_INFO['CLIENT_ID'],
        client_secret=CLIENT_OAUTH2_INFO['CLIENT_SECRET'],
        token_url=CLIENT_OAUTH2_INFO['TOKEN_URL'],
        refresh_url=CLIENT_OAUTH2_INFO['REFRESH_URL'],
        auth_url=CLIENT_OAUTH2_INFO['AUTH_URL'],
        scope=CLIENT_OAUTH2_INFO['SCOPE'],
        user_email=CLIENT_OAUTH2_INFO['EMAIL'],
        base_api_url=BASE_API_URL)

    db_cal_const_1 = {
        'calibration_constant': {
            'name': 'CALIBRATION_CONSTANT_TEST-1_DO_NOT_DELETE',
            'calibration_id': '-1',
            'device_type_id': '-1',
            'condition_id': '-1',
            'description': 'Created automatically via seed:seed_tests'
        }
    }
    db_cal_const_2 = {
        'calibration_constant': {
            'name': 'CALIBRATION_CONSTANT_TEST-2_DO_NOT_DELETE',
            'calibration_id': '-1',
            'device_type_id': '-1',
            'condition_id': '-2',
            'description': 'Created automatically via seed:seed_tests'
        }
    }

    def test_create_calibration_constant_api(self):
        __unique_name = Generators.generate_unique_name('CConstantApi')
        calibration_const = {
            'calibration_constant': {
                'name': __unique_name,
                'calibration_id': '-2',
                'device_type_id': '-1',
                'condition_id': '-1',
                'flg_auto_approve': 'true',
                'flg_available': 'true',
                'description': 'desc 01'
            }
        }

        expect = calibration_const['calibration_constant']

        expect_db_all = [self.db_cal_const_1['calibration_constant'],
                         self.db_cal_const_2['calibration_constant']]

        #
        # Create new entry (should succeed)
        #
        received = self.__create_entry_api(calibration_const, expect)

        cal_constant_id = received['id']
        cal_constant_name = received['name']

        #
        # Create duplicated entry (should throw an error)
        #
        self.__create_error_entry_uk_api(calibration_const)

        #
        # Get entry by all calibration constants (should succeed)
        #
        condition_ids = [
            self.db_cal_const_1['calibration_constant']['condition_id'],
            self.db_cal_const_2['calibration_constant']['condition_id']]

        self.__get_all_calibration_constants_by_conditions_api(
            self.db_cal_const_1['calibration_constant']['calibration_id'],
            self.db_cal_const_1['calibration_constant']['device_type_id'],
            condition_ids,
            expect_db_all)

        #
        # Get entry by it's Unique Key (UK) (should succeed)
        #
        self.__get_entry_by_uk_api(calibration_const, expect)

        #
        # Get entry by it's Unique Key (UK) (should not_found)
        #
        self.__get_entry_by_uk_api_not_found_api()

        #
        # Get entry by name
        #
        self.__get_all_entries_by_name_api(cal_constant_name, expect)

        #
        # Get entry by ID
        #
        self.__get_entry_by_id_api(cal_constant_id, expect)

        #
        # Put entry information (update some fields should succeed)
        #
        self.__update_entry_api(cal_constant_id, expect)

        #
        # Delete entry (should succeed)
        # (test purposes only to keep the DB clean)
        #
        self.__delete_entry_by_id_api(cal_constant_id)

    #
    # fields_validation
    #
    def fields_validation(self, receive, expect):
        self.assert_eq_hfield(receive, expect, 'name', STRING)
        self.assert_eq_hfield(receive, expect, 'device_type_id', NUMBER)
        self.assert_eq_hfield(receive, expect, 'calibration_id', NUMBER)
        self.assert_eq_hfield(receive, expect, 'condition_id', NUMBER)
        self.assert_eq_hfield(receive, expect, 'flg_auto_approve', BOOLEAN)
        self.assert_eq_hfield(receive, expect, 'flg_available', BOOLEAN)
        self.assert_eq_hfield(receive, expect, 'description', STRING)

    #
    # Internal private APIs methods
    #
    def __create_entry_api(self, entry_info, expect):
        response = self.cal_client_api.create_calibration_constant_api(
            entry_info)
        receive = self.get_and_validate_create_entry(response)
        self.fields_validation(receive, expect)
        return receive

    def __create_error_entry_uk_api(self, entry_info):
        response = self.cal_client_api.create_calibration_constant_api(
            entry_info)
        resp_content = self.load_response_content(response)

        receive = resp_content
        expect = {
            'info': {
                'name': ['has already been taken'],
                'device_type': ['has already been taken'],
                'calibration': ['has already been taken'],
                'condition': ['has already been taken']
            }
        }

        self.assertEqual(receive, expect, "Expected result not received")
        self.assert_eq_status_code(response.status_code, UNPROCESSABLE_ENTITY)

        # 'has already been taken'
        receive_msg_name = receive['info']['name'][0]
        expect_msg_name = expect['info']['name'][0]
        self.assert_eq_str(receive_msg_name, expect_msg_name)

        # 'has already been taken'
        receive_msg = receive['info']['device_type'][0]
        expect_msg = expect['info']['device_type'][0]
        self.assert_eq_str(receive_msg, expect_msg)

        # 'has already been taken'
        receive_msg = receive['info']['calibration'][0]
        expect_msg = expect['info']['calibration'][0]
        self.assert_eq_str(receive_msg, expect_msg)

        # 'has already been taken'
        receive_msg = receive['info']['condition'][0]
        expect_msg = expect['info']['condition'][0]
        self.assert_eq_str(receive_msg, expect_msg)

    def __update_entry_api(self, entry_id, expect):
        unique_name = Generators.generate_unique_name('CConstantApiUpd')
        calibration_const_upd = {
            'calibration_constant': {
                'name': unique_name,
                # 'calibration_id': '-2',
                # 'device_type_id': '-1',
                # 'condition_id': '-1',
                'flg_auto_approve': 'false',
                'flg_available': 'false',
                'description': 'desc 01 updated!'
            }
        }

        resp = self.cal_client_api.update_calibration_constant_api(
            entry_id,
            calibration_const_upd
        )

        resp_content = self.load_response_content(resp)

        receive = resp_content

        # Add parameters not send to the update API
        calibration_const_upd['calibration_constant']['calibration_id'] = '-2'
        calibration_const_upd['calibration_constant']['device_type_id'] = '-1'
        calibration_const_upd['calibration_constant']['condition_id'] = '-1'
        expect_upd = calibration_const_upd['calibration_constant']

        self.fields_validation(receive, expect_upd)
        self.assert_eq_status_code(resp.status_code, OK)

        field = 'name'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'flg_auto_approve'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'flg_available'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'description'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)

    def __get_all_entries_by_name_api(self, name, expect):
        resp = self.cal_client_api.get_all_calibration_constants_by_name_api(
            name
        )

        receive = self.get_and_validate_all_entries_by_name(resp)
        self.fields_validation(receive, expect)

    def __get_entry_by_id_api(self, entry_id, expect):
        resp = self.cal_client_api.get_calibration_constant_by_id_api(entry_id)
        receive = self.get_and_validate_entry_by_id(resp)
        self.fields_validation(receive, expect)

    def __get_entry_by_uk_api(self, entry, expect):
        resp = self.cal_client_api.get_calibration_constant_by_uk_api(
            entry['calibration_constant']['calibration_id'],
            entry['calibration_constant']['device_type_id'],
            entry['calibration_constant']['condition_id'])

        resp_content = self.load_response_content(resp)

        receive = resp_content

        self.fields_validation(receive, expect)
        self.assert_eq_status_code(resp.status_code, OK)

    def __get_entry_by_uk_api_not_found_api(self):
        calibration_id = -99
        dev_type_id = -99
        cond_id = -99

        resp = self.cal_client_api.get_calibration_constant_by_uk_api(
            calibration_id,
            dev_type_id,
            cond_id
        )

        self.get_and_validate_resource_not_found(resp)

    def __get_all_calibration_constants_by_conditions_api(self,
                                                          calibration_id,
                                                          device_type_id,
                                                          condition_ids,
                                                          expect):
        resp = self.cal_client_api.get_all_calibration_constants_by_conds_api(
            calibration_id, device_type_id, condition_ids)

        resp_content = self.load_response_content(resp)

        receive = resp_content

        self.assertEqual(len(receive), len(receive), 'Array size should be 2')
        self.assertEqual(
            receive[0]['name'],
            self.db_cal_const_2['calibration_constant']['name'],
            'Name of first calibration constant should match')
        self.assertEqual(
            receive[1]['name'],
            self.db_cal_const_1['calibration_constant']['name'],
            'Name of first calibration constant should match')

        self.assert_eq_status_code(resp.status_code, OK)

    def __delete_entry_by_id_api(self, entry_id):
        resp = self.cal_client_api.delete_calibration_constant_api(entry_id)
        self.get_and_validate_delete_entry_by_id(resp)


if __name__ == '__main__':
    unittest.main()
