"""CalibrationConstantVersionApiTest class"""

import unittest

from .api_base import ApiBase
from ..common.config_test import *
from ..common.generators import Generators
from ..common.secrets import *
from ...calibration_client_api import CalibrationClientApi


class CalibrationConstantVersionApiTest(ApiBase, unittest.TestCase):
    cal_client_api = CalibrationClientApi(
        client_id=CLIENT_OAUTH2_INFO['CLIENT_ID'],
        client_secret=CLIENT_OAUTH2_INFO['CLIENT_SECRET'],
        token_url=CLIENT_OAUTH2_INFO['TOKEN_URL'],
        refresh_url=CLIENT_OAUTH2_INFO['REFRESH_URL'],
        auth_url=CLIENT_OAUTH2_INFO['AUTH_URL'],
        scope=CLIENT_OAUTH2_INFO['SCOPE'],
        user_email=CLIENT_OAUTH2_INFO['EMAIL'],
        base_api_url=BASE_API_URL)

    __unique_name = Generators.generate_unique_name('CCVersionApi')
    __unique_file_name = Generators.generate_unique_file_name()
    __begin_at = Generators.generate_timestamp_str(0)

    __calibration_constant_version_01 = {
        'calibration_constant_version': {
            'name': __unique_name,
            'file_name': __unique_file_name,
            'path_to_file': 'path_to_file_1',
            'data_set_name': 'data_set_name_1',
            'calibration_constant_id': '-3',
            'physical_device_id': '-1',
            'flg_deployed': 'true',
            'flg_good_quality': 'true',
            'begin_validity_at': '2014-05-25T08:30:00.000+02:00',
            'end_validity_at': '2025-12-25T08:30:00.000+01:00',
            'begin_at': __begin_at,
            'start_idx': '1',
            'end_idx': '2',
            'raw_data_location': 'XFEL/metadata/',
            'description': 'desc version 01'
        }
    }

    def test_create_calibration_constant_version_api(self):
        ccv = self.__calibration_constant_version_01
        expect = ccv['calibration_constant_version']

        #
        # Create new entry (should succeed)
        #
        received = self.__create_entry_api(ccv, expect)

        ccv_id = received['id']
        ccv_name = received['name']

        #
        # Create duplicated entry (should throw an error)
        #
        self.__create_error_entry_uk_api(ccv)

        # event_at == expected_hash['begin_at']
        # This is necessary, because the CalibrationConstantVersionApi.begin_at
        # current_DATETIME + Random(60 seconds) is part of the Unique Key that
        # identifies uniquely a Calibration Constant Version entry
        self.__test_get_version_int(expect['begin_at'],
                                    expect_ccv_id=ccv_id)

        #
        # Get entry by name
        #
        self.__get_all_entries_by_name_api(ccv_name, expect)

        #
        # Get entry by ID
        #
        self.__get_entry_by_id_api(ccv_id, expect)

        #
        # Put entry information (update some fields should succeed)
        #
        self.__update_entry_api(ccv_id, expect)

    #
    # fields_validation
    #
    def fields_validation(self, receive, expect):
        self.assert_eq_hfield(receive, expect, 'name', STRING)
        self.assert_eq_hfield(receive, expect, 'file_name', STRING)
        self.assert_eq_hfield(receive, expect, 'path_to_file', STRING)
        self.assert_eq_hfield(receive, expect, 'data_set_name', STRING)
        self.assert_eq_hfield(receive, expect, 'flg_deployed', BOOLEAN)
        self.assert_eq_hfield(receive, expect, 'flg_good_quality', BOOLEAN)
        self.assert_eq_hfield(receive, expect, 'begin_at', DATETIME)
        self.assert_eq_hfield(receive, expect, 'begin_validity_at', DATETIME)
        self.assert_eq_hfield(receive, expect, 'end_validity_at', DATETIME)

        self.assert_eq_hfield(receive, expect, 'start_idx', NUMBER)
        self.assert_eq_hfield(receive, expect, 'end_idx', NUMBER)
        self.assert_eq_hfield(receive, expect, 'raw_data_location', STRING)
        self.assert_eq_hfield(receive, expect, 'description', STRING)

        receive_cc_id = receive['calibration_constant']['id']
        self.assert_eq_val(receive_cc_id, expect['calibration_constant_id'])

        receive_cc_id = receive[PHYSICAL_DEVICE]['id']
        self.assert_eq_val(receive_cc_id, expect['physical_device_id'])

    #
    # Internal private APIs methods
    #
    def __create_entry_api(self, entry_info, expect):
        response = self.cal_client_api.create_calibration_constant_version_api(
            entry_info)
        receive = self.get_and_validate_create_entry(response)
        self.fields_validation(receive, expect)
        return receive

    def __create_error_entry_uk_api(self, entry_info):
        response = self.cal_client_api.create_calibration_constant_version_api(
            entry_info)
        resp_content = self.load_response_content(response)

        receive = resp_content
        expect = {'info': {'name': ['has already been taken'],
                           'calibration_constant_id': [
                               'has already been taken',
                               'has already been taken'],
                           'physical_device_id': ['has already been taken'],
                           'begin_at': ['has already been taken']}}

        self.assertEqual(receive, expect, "Expected result not received")
        self.assert_eq_status_code(response.status_code, UNPROCESSABLE_ENTITY)

        # 'has already been taken'
        receive_msg_name = receive['info']['name'][0]
        expect_msg_name = expect['info']['name'][0]
        self.assert_eq_str(receive_msg_name, expect_msg_name)

        # 'has already been taken'
        receive_msg = receive['info']['calibration_constant_id'][0]
        expect_msg = expect['info']['calibration_constant_id'][0]
        self.assert_eq_str(receive_msg, expect_msg)

        # 'has already been taken'
        receive_msg = receive['info']['physical_device_id'][0]
        expect_msg = expect['info']['physical_device_id'][0]
        self.assert_eq_str(receive_msg, expect_msg)

        # 'has already been taken'
        receive_msg = receive['info']['begin_at'][0]
        expect_msg = expect['info']['begin_at'][0]
        self.assert_eq_str(receive_msg, expect_msg)

    def __test_get_version_int(self, event_at, expect_ccv_id=None):
        ccv = self.__calibration_constant_version_01
        expect = ccv['calibration_constant_version']

        calibration_constant_id = expect['calibration_constant_id']
        physical_device_id = expect['physical_device_id']
        # event_at = '' #'2014-10-13T09:13:26.000+02:00'
        snapshot_at = ''

        resp = self.cal_client_api.get_calibration_constant_version_by_uk_api(
            calibration_constant_id, physical_device_id, event_at, snapshot_at)
        resp_content = self.load_response_content(resp)

        receive = resp_content

        self.fields_validation(receive, expect)
        self.assert_eq_status_code(resp.status_code, OK)

        if expect_ccv_id is not None:
            receive_id = receive['id']
            self.assert_eq_val(receive_id, expect_ccv_id)

    def __get_all_entries_by_name_api(self, name, expect):
        resp = self.cal_client_api. \
            get_all_calibration_constant_versions_by_name_api(name)

        receive = self.get_and_validate_all_entries_by_name(resp)
        self.fields_validation(receive, expect)

    def __get_entry_by_id_api(self, entry_id, expect):
        resp = self.cal_client_api.get_calibration_constant_version_by_id_api(
            entry_id)
        receive = self.get_and_validate_entry_by_id(resp)
        self.fields_validation(receive, expect)

    def __update_entry_api(self, entry_id, expect):
        __unique_name = Generators.generate_unique_name('CCVersionApiUpd')
        __unique_file_name = Generators.generate_unique_file_name()
        __begin_at = Generators.generate_timestamp_str(1)
        ccv_upd = {
            'calibration_constant_version': {
                'name': __unique_name,
                'file_name': __unique_file_name,
                'path_to_file': 'path_to_file_2',
                'data_set_name': 'data_set_name_2',
                # 'calibration_constant_id': '-1',
                # 'physical_device_id': '-1',
                'flg_deployed': 'false',
                'flg_good_quality': 'false',
                'begin_validity_at': '2014-05-25T08:31:00.000+02:00',
                'end_validity_at': '2025-12-25T08:31:00.000+01:00',
                'begin_at': __begin_at,
                'start_idx': '10',
                'end_idx': '20',
                'raw_data_location': 'XFEL/metadata_bck/',
                'description': 'desc version 01 UPDATED!'
            }
        }

        response = self.cal_client_api.update_calibration_constant_version_api(
            entry_id,
            ccv_upd)

        resp_content = self.load_response_content(response)

        receive = resp_content

        # Add parameters not send to the update API
        expect_upd = ccv_upd['calibration_constant_version']
        expect_upd['calibration_constant_id'] = '-3'
        expect_upd['physical_device_id'] = '-1'

        self.fields_validation(receive, expect_upd)
        self.assert_eq_status_code(response.status_code, OK)

        field = 'name'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'file_name'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'path_to_file'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'data_set_name'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'flg_deployed'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'flg_good_quality'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'begin_validity_at'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'end_validity_at'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'begin_at'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'start_idx'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'end_idx'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'raw_data_location'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'description'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)


if __name__ == '__main__':
    unittest.main()
