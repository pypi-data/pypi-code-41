"""CalibrationConstantVersionTest class"""

import unittest

from calibration_client.calibration_client import CalibrationClient
from .module_base import ModuleBase
from ..common.config_test import *
from ..common.generators import Generators
from ..common.secrets import *
from ...modules.calibration_constant_version import CalibrationConstantVersion

MODULE_NAME = CALIBRATION_CONSTANT_VERSION


class CalibrationConstantVersionTest(ModuleBase, unittest.TestCase):
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

        __unique_name = Generators.generate_unique_name('CCV_01')
        __unique_file_name = Generators.generate_unique_file_name()
        __begin_at = Generators.generate_timestamp_str(0)

        self.ccv_01 = {
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

        __unique_name_upd = Generators.generate_unique_name('CCVersionUpd01')
        __unique_file_name_upd = Generators.generate_unique_file_name()
        __new_begin_at = -(60 * 60 * 24)  # Minus 1 day
        __begin_at_upd = Generators.generate_timestamp_str(__new_begin_at)

        self.ccv_01_upd = {
            'name': __unique_name_upd,
            'file_name': __unique_file_name_upd,
            'path_to_file': 'path_to_file_1_upd',
            'data_set_name': 'data_set_name_1_upd',
            'calibration_constant_id': '-3',
            'physical_device_id': '-1',
            'flg_deployed': 'false',
            'flg_good_quality': 'false',
            'begin_validity_at': '2014-06-25T08:30:00.000+02:00',
            'end_validity_at': '2025-11-25T08:30:00.000+01:00',
            'begin_at': __begin_at_upd,
            'start_idx': '0',
            'end_idx': '1',
            'raw_data_location': 'XFEL/metadata/bck/',
            'description': 'desc version 01 Updated!'
        }

        self.expected_db_02 = {
            'id': -2,
            'name': 'CALIBRATION_CONSTANT_VERSION_TEST-2_DO_NOT_DELETE',
            'file_name': 'cal.r0001.c0002.h5',
            'path_to_file': '/usr/local/cal_repo/',
            'data_set_name': 'exp001.cal001',
            'flg_deployed': True,
            'flg_good_quality': True,
            'begin_validity_at': '2014-05-25T10:30:14.000+02:00',
            'end_validity_at': '2029-06-24T00:00:00.000+02:00',
            'begin_at': '2014-05-26T12:00:00.000+02:00',
            'start_idx': None,
            'end_idx': None,
            'raw_data_location': None,
            'description': None,
            # 'calibration_constant': {
            #     'id': -1,
            #     'name': 'CALIBRATION_CONSTANT_TEST-1_DO_NOT_DELETE',
            #     'flg_auto_approve': True,
            #     'flg_available': True,
            #     'description': 'Created automatically via seed:seed_tests',
            #     'device_type_id': -1,
            #     'calibration_id': -1,
            #     'condition_id': -1},
            'calibration_constant_id': -1,
            # 'physical_device': {
            #     'id': -1,
            #     'name': 'PHYSICAL_DEVICE-1_DO_NOT_DELETE',
            #     'device_type_id': -1,
            #     'flg_available': True,
            #     'parent_id': None,
            #     'description': 'Created automatically via seed:seed_tests'}
            'physical_device_id': -1}

        self.expected_db_04 = {
            'id': -4,
            'name': 'CALIBRATION_CONSTANT_VERSION_TEST-4_DO_NOT_DELETE',
            'file_name': 'cal.r0001.c0002.h5',
            'path_to_file': '/usr/local/cal_repo/',
            'data_set_name': 'exp001.cal001',
            'flg_deployed': True,
            'flg_good_quality': True,
            'begin_validity_at': '2015-05-25T10:30:14.000+02:00',
            'end_validity_at': '2029-06-24T00:00:00.000+02:00',
            'begin_at': '2015-05-26T12:00:00.000+02:00',
            'start_idx': None,
            'end_idx': None,
            'raw_data_location': None,
            'description': None,
            # 'calibration_constant': {
            #     'id': -2,
            #     'name': 'CALIBRATION_CONSTANT_TEST-2_DO_NOT_DELETE',
            #     'flg_auto_approve': True,
            #     'flg_available': True,
            #     'description': 'Created automatically via seed:seed_tests',
            #     'device_type_id': -1,
            #     'calibration_id': -1,
            #     'condition_id': -2},
            'calibration_constant_id': -2,
            # 'physical_device': {
            #     'id': -1,
            #     'name': 'PHYSICAL_DEVICE-1_DO_NOT_DELETE',
            #     'device_type_id': -1,
            #     'flg_available': True,
            #     'parent_id': None,
            #     'description': 'Created automatically via seed:seed_tests'}
            'physical_device_id': -1}

    def test_create_calibration_constant_version(self):
        __begin_at = Generators.generate_timestamp_str(0)

        __new_begin_at = -(60 * 60 * 24)  # Minus 1 day
        __begin_at_upd = Generators.generate_timestamp_str(__new_begin_at)

        ccv_01 = CalibrationConstantVersion(
            calibration_client=self.cal_client,
            name=self.ccv_01['name'],
            file_name=self.ccv_01['file_name'],
            path_to_file=self.ccv_01['path_to_file'],
            data_set_name=self.ccv_01['data_set_name'],
            calibration_constant_id=self.ccv_01['calibration_constant_id'],
            physical_device_id=self.ccv_01['physical_device_id'],
            flg_deployed=self.ccv_01['flg_deployed'],
            flg_good_quality=self.ccv_01['flg_good_quality'],
            begin_validity_at=self.ccv_01['begin_validity_at'],
            end_validity_at=self.ccv_01['end_validity_at'],
            begin_at=__begin_at,
            start_idx=self.ccv_01['start_idx'],
            end_idx=self.ccv_01['end_idx'],
            raw_data_location=self.ccv_01['raw_data_location'],
            description=self.ccv_01['description']
        )

        #
        # Create new entry (should succeed)
        #
        result1 = ccv_01.create()
        self.assert_create_success(MODULE_NAME, result1, self.ccv_01)

        calibration_constant_version = result1['data']
        ccv_id = calibration_constant_version['id']
        ccv_name = calibration_constant_version['name']
        ccv_cc_id = calibration_constant_version['calibration_constant']['id']
        ccv_pd_id = calibration_constant_version['physical_device']['id']

        #
        # Create duplicated entry (should throw an error)
        #
        ccv_01_dup = ccv_01
        result2 = ccv_01_dup.create()
        expect_app_info = {'name': ['has already been taken']}
        self.assert_create_error(MODULE_NAME, result2, expect_app_info)

        #
        # Get entry by name
        #
        result3 = CalibrationConstantVersion.get_by_name(self.cal_client,
                                                         ccv_name)
        self.assert_find_success(MODULE_NAME, result3, self.ccv_01)

        #
        # Get entry by ID
        #
        result4 = CalibrationConstantVersion.get_by_id(self.cal_client, ccv_id)
        self.assert_find_success(MODULE_NAME, result4, self.ccv_01)

        #
        # Get entry with non-existent ID (should throw an error)
        #
        ccv_id = -666
        result5 = CalibrationConstantVersion.get_by_id(self.cal_client, ccv_id)
        self.assert_find_error(MODULE_NAME, result5, RESOURCE_NOT_FOUND)

        #
        # Get entry by UK (should succeed)
        # (calibration_constant_id, physical_device_id, event_at, snapshot_at)
        #
        ccv_event_at = calibration_constant_version['begin_at']
        ccv_snapshot_at = ''  # '' == Now()

        result_uk = CalibrationConstantVersion.get_by_uk(self.cal_client,
                                                         ccv_cc_id,
                                                         ccv_pd_id,
                                                         ccv_event_at,
                                                         ccv_snapshot_at)
        self.assert_find_success(MODULE_NAME, result_uk, self.ccv_01)

        #
        # Get entry by UK (should throw an error)
        # (calibration_constant_id, physical_device_id, event_at, snapshot_at)
        #
        calibration_constant_id = -666
        physical_device_id = -666
        ccv_event_at = ''  # '' == Now()
        ccv_snapshot_at = ''  # '' == Now()

        res_uk_error = CalibrationConstantVersion.get_by_uk(
            self.cal_client,
            calibration_constant_id,
            physical_device_id,
            ccv_event_at,
            ccv_snapshot_at
        )
        self.assert_find_error(MODULE_NAME, res_uk_error, RESOURCE_NOT_FOUND)

        #
        # Put entry information (update some fields should succeed)
        #
        ccv_01.name = self.ccv_01_upd['name']
        ccv_01.file_name = self.ccv_01_upd['file_name']
        ccv_01.path_to_file = self.ccv_01_upd['path_to_file']
        ccv_01.data_set_name = self.ccv_01_upd['data_set_name']
        ccv_01.flg_deployed = self.ccv_01_upd['flg_deployed']
        ccv_01.flg_good_quality = self.ccv_01_upd['flg_good_quality']
        ccv_01.begin_validity_at = self.ccv_01_upd['begin_validity_at']
        ccv_01.end_validity_at = self.ccv_01_upd['end_validity_at']
        ccv_01.begin_at = __begin_at_upd
        ccv_01.start_idx = self.ccv_01_upd['start_idx']
        ccv_01.end_idx = self.ccv_01_upd['end_idx']
        ccv_01.raw_data_location = self.ccv_01_upd['raw_data_location']
        ccv_01.description = self.ccv_01_upd['description']
        result6 = ccv_01.update()
        self.assert_update_success(MODULE_NAME, result6, self.ccv_01_upd)

        #
        # Put entry information (update some fields should throw an error)
        #
        ccv_01.name = '__THIS_NAME_IS_1_CHARACTERS_LONGER_THAN_THE_ALLOWED_MAX_NUM__'  # noqa
        result7 = ccv_01.update()
        expect_app_info = {'name': ['is too long (maximum is 60 characters)']}
        self.assert_update_error(MODULE_NAME, result7, expect_app_info)

        #
        # Delete entry (should succeed)
        # (test purposes only to keep the DB clean)
        #
        # result8 = ccv_01.delete()
        # self.assert_delete_success(MODULE_NAME, result8)

        #
        # Delete entry (should throw an error)
        # (test purposes only to keep the DB clean)
        #
        # result9 = ccv_01.delete()
        # self.assert_delete_error(MODULE_NAME, result9, RESOURCE_NOT_FOUND)

    def test_create_calibration_constant_version_from_dict(self):
        #
        # Create new entry (should succeed)
        #
        result1 = CalibrationConstantVersion.create_from_dict(self.cal_client,
                                                              self.ccv_01)
        self.assert_create_success(MODULE_NAME, result1, self.ccv_01)

        calibration_constant_version = result1['data']
        ccv_id = calibration_constant_version['id']
        ccv_name = calibration_constant_version['name']

        #
        # Create duplicated entry (should throw an error)
        #
        result2 = CalibrationConstantVersion.create_from_dict(self.cal_client,
                                                              self.ccv_01)
        expect_app_info = {'name': ['has already been taken']}
        self.assert_create_error(MODULE_NAME, result2, expect_app_info)

        #
        # Get entry by name
        #
        result3 = CalibrationConstantVersion.get_by_name(self.cal_client,
                                                         ccv_name)
        self.assert_find_success(MODULE_NAME, result3, self.ccv_01)

        #
        # Get entry by ID
        #
        result4 = CalibrationConstantVersion.get_by_id(self.cal_client, ccv_id)
        self.assert_find_success(MODULE_NAME, result4, self.ccv_01)

    def test_calibration_constants_get_closest_version_now(self):
        #
        # Search for the closest version
        #
        calibration_constant_ids = [-1, -2]
        physical_device_id = -1
        event_at = None
        snapshot_at = None

        result1 = CalibrationConstantVersion.get_closest_by_time(
            self.cal_client, calibration_constant_ids, physical_device_id,
            event_at, snapshot_at)

        # result1 ==>
        # {'success': True,
        #  'info': 'Got calibration_constant_version successfully',
        #  'app_info': {},
        #  'data': {
        #       'id': -4,
        #       'name': 'CALIBRATION_CONSTANT_VERSION_TEST-4_DO_NOT_DELETE',
        #       'file_name': 'cal.r0001.c0002.h5',
        #       'path_to_file': '/usr/local/cal_repo/',
        #       'data_set_name': 'exp001.cal001',
        #       'flg_deployed': True,
        #       'flg_good_quality': True,
        #       'begin_validity_at': '2015-05-25T10:30:14.000+02:00',
        #       'end_validity_at': '2029-06-24T00:00:00.000+02:00',
        #       'begin_at': '2015-05-26T12:00:00.000+02:00',
        #       'start_idx': None,
        #       'end_idx': None,
        #       'raw_data_location': None,
        #       'description': None,
        #       'calibration_constant': {
        #           'id': -2,
        #           'name': 'CALIBRATION_CONSTANT_TEST-2_DO_NOT_DELETE',
        #           'flg_auto_approve': True,
        #           'flg_available': True,
        #           'description': 'Created automatically via seed:seed_tests',
        #           'device_type_id': -1,
        #           'calibration_id': -1,
        #           'condition_id': -2},
        #       'physical_device': {
        #           'id': -1,
        #           'name': 'PHYSICAL_DEVICE-1_DO_NOT_DELETE',
        #           'device_type_id': -1,
        #           'flg_available': True,
        #           'parent_id': None,
        #           'description': 'Created automatically via seed:seed_tests'}
        # }}

        self.assert_find_success(MODULE_NAME, result1, self.expected_db_04)

    def test_calibration_constants_get_closest_version_in_the_past(self):
        #
        # Search for the closest version
        #
        calibration_constant_ids = [-1, -2]
        physical_device_id = -1
        event_at = '2014-05-26T12:00:00.000+02:00'
        snapshot_at = None

        result1 = CalibrationConstantVersion.get_closest_by_time(
            self.cal_client, calibration_constant_ids, physical_device_id,
            event_at, snapshot_at)

        # result1 ==>
        # {'success': True,
        #  'info': 'Got calibration_constant_version successfully',
        #  'app_info': {},
        #  'data': {
        #       'id': -2,
        #       'name': 'CALIBRATION_CONSTANT_VERSION_TEST-2_DO_NOT_DELETE',
        #       'file_name': 'cal.r0001.c0002.h5',
        #       'path_to_file': '/usr/local/cal_repo/',
        #       'data_set_name': 'exp001.cal001',
        #       'flg_deployed': True,
        #       'flg_good_quality': True,
        #       'begin_validity_at': '2014-05-25T10:30:14.000+02:00',
        #       'end_validity_at': '2029-06-24T00:00:00.000+02:00',
        #       'begin_at': '2014-05-26T12:00:00.000+02:00',
        #       'start_idx': None,
        #       'end_idx': None,
        #       'raw_data_location': None,
        #       'description': None,
        #       'calibration_constant': {
        #           'id': -1,
        #           'name': 'CALIBRATION_CONSTANT_TEST-1_DO_NOT_DELETE',
        #           'flg_auto_approve': True,
        #           'flg_available': True,
        #           'description': 'Created automatically via seed:seed_tests',
        #           'device_type_id': -1,
        #           'calibration_id': -1,
        #           'condition_id': -1},
        #       'physical_device': {
        #           'id': -1,
        #           'name': 'PHYSICAL_DEVICE-1_DO_NOT_DELETE',
        #           'device_type_id': -1,
        #           'flg_available': True,
        #           'parent_id': None,
        #           'description': 'Created automatically via seed:seed_tests'}
        # }}

        self.assert_find_success(MODULE_NAME, result1, self.expected_db_02)

    def test_calibration_constants_get_all_versions_now(self):
        #
        # Search for all the version
        #
        calibration_constant_ids = [-1, -2]
        physical_device_id = -1
        event_at = None
        snapshot_at = None

        result1 = CalibrationConstantVersion.get_all_versions(
            self.cal_client, calibration_constant_ids, physical_device_id,
            event_at, snapshot_at)

        self.assert_eq_val(len(result1['data']), 4)

        self.assert_eq_val(result1['data'][0]['id'], -4)
        self.assert_eq_val(result1['data'][0]['name'],
                           self.expected_db_04['name'])

        self.assert_eq_val(result1['data'][1]['id'], -3)
        self.assert_eq_val(result1['data'][1]['name'],
                           'CALIBRATION_CONSTANT_VERSION_TEST-3_DO_NOT_DELETE')

        self.assert_eq_val(result1['data'][2]['id'], -2)
        self.assert_eq_val(result1['data'][2]['name'],
                           self.expected_db_02['name'])

        self.assert_eq_val(result1['data'][3]['id'], -1)
        self.assert_eq_val(result1['data'][3]['name'],
                           'CALIBRATION_CONSTANT_VERSION_TEST-1_DO_NOT_DELETE')

    def test_calibration_constants_get_all_versions_in_the_past(self):
        #
        # Search for all the version
        #
        calibration_constant_ids = [-1, -2]
        physical_device_id = -1
        event_at = '2014-05-26T12:00:00.000+02:00'
        snapshot_at = None

        result1 = CalibrationConstantVersion.get_all_versions(
            self.cal_client, calibration_constant_ids, physical_device_id,
            event_at, snapshot_at)

        self.assert_eq_val(len(result1['data']), 4)

        self.assert_eq_val(result1['data'][0]['id'], -2)
        self.assert_eq_val(result1['data'][0]['name'],
                           self.expected_db_02['name'])

        self.assert_eq_val(result1['data'][1]['id'], -1)
        self.assert_eq_val(result1['data'][1]['name'],
                           'CALIBRATION_CONSTANT_VERSION_TEST-1_DO_NOT_DELETE')

        self.assert_eq_val(result1['data'][2]['id'], -3)
        self.assert_eq_val(result1['data'][2]['name'],
                           'CALIBRATION_CONSTANT_VERSION_TEST-3_DO_NOT_DELETE')

        self.assert_eq_val(result1['data'][3]['id'], -4)
        self.assert_eq_val(result1['data'][3]['name'],
                           self.expected_db_04['name'])

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


if __name__ == '__main__':
    unittest.main()
