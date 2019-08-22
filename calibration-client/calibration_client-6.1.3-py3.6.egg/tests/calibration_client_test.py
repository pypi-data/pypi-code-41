"""CalibrationClientTest class"""

import logging
import unittest

from calibration_client.calibration_client import CalibrationClient
from .calibration_test_hash import CalibrationTestHash
from .common.config_test import *
from .common.secrets import *
from .modules.module_base import ModuleBase


class CalibrationClientTest(ModuleBase, unittest.TestCase):
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

        self.existing_db_05 = {
            'id': -5,
            'name': 'CALIBRATION_CONSTANT_VERSION_TEST-5_DO_NOT_DELETE',
            'begin_at': '2016-05-24T12:00:00.000+02:00',
            'file_name': 'cal.r0001.c0001.h5',
            'path_to_file': '/usr/local/cal_repo/',
            'data_set_name': 'exp001.cal001',
            'raw_data_location': None,
            'calibration_constant_id': -3,
            'physical_device_id': -1,
            'flg_deployed': True,
            'flg_good_quality': True,
            'begin_validity_at': '2016-05-24T10:30:14.000+02:00',
            'end_validity_at': '2029-06-24T00:00:00.000+02:00',
            'start_idx': None,
            'end_idx': None,
            'description': None}

        self.existing_db_06 = {
            'id': -6,
            'name': 'CALIBRATION_CONSTANT_VERSION_TEST-6_DO_NOT_DELETE',

            'begin_at': '2016-05-26T12:00:00.000+02:00',
            'file_name': 'cal.r0001.c0002.h5',
            'path_to_file': '/usr/local/cal_repo/',
            'data_set_name': 'exp001.cal001',
            'raw_data_location': None,
            'calibration_constant_id': -3,
            'physical_device_id': -1,
            'flg_deployed': True,
            'flg_good_quality': True,
            'begin_validity_at': '2016-05-25T10:30:14.000+02:00',
            'end_validity_at': '2029-06-24T00:00:00.000+02:00',
            'start_idx': None,
            'end_idx': None,
            'description': None}

    def test_inject_new_calibration_constant_version(self):
        calibration_hash_01 = CalibrationTestHash(None).valid_01

        cal_dict = calibration_hash_01['karabo_h']
        det_cond_h = cal_dict['detector_condition']
        cc_h = cal_dict['calibration_constant']
        ccv_h = cal_dict['calibration_constant_version']
        #
        begin_at_exp = calibration_hash_01['begin_at_exp']
        begin_val_at_exp = calibration_hash_01['begin_validity_at_exp']
        end_val_at_exp = calibration_hash_01['end_validity_at_exp']

        cal_inject_dict = {
            'detector_condition': det_cond_h,
            'calibration_constant': cc_h,
            'calibration_constant_version': ccv_h
        }

        resp = CalibrationClient.inject_new_calibration_constant_version(
            self.cal_client,
            cal_inject_dict
        )

        # Logging information
        logging.error('calibration_hash_01: {0}'.format(calibration_hash_01))
        logging.error('cal_inject_dict: {0}'.format(cal_inject_dict))
        logging.error('resp: {0}'.format(resp))

        self.assert_eq_val(resp['app_info'], {})
        self.assert_eq_val(resp['success'], True)

        success_info_msg = 'calibration_constant_version created successfully'
        self.assert_eq_val(resp['info'], success_info_msg)

        # Calibration Constant Version info
        resp_ccv = resp['data']
        self.assert_eq_val(resp_ccv['name'], ccv_h['name'])
        self.assert_eq_val(resp_ccv['flg_good_quality'], True)

        self.assert_eq_val(resp_ccv['begin_validity_at'], begin_val_at_exp)
        self.assert_eq_val(resp_ccv['end_validity_at'], end_val_at_exp)
        self.assert_eq_val(resp_ccv['begin_at'], begin_at_exp)

        self.assert_eq_val(resp_ccv['flg_deployed'], True)
        self.assert_eq_val(resp_ccv['raw_data_location'],
                           ccv_h['raw_data_location'])
        self.assert_eq_val(resp_ccv['file_name'], ccv_h['file_name'])
        self.assert_eq_val(resp_ccv['path_to_file'], ccv_h['path_to_file'])
        self.assert_eq_val(resp_ccv['description'], ccv_h['description'])
        # Special cases...
        self.assert_eq_val(resp_ccv['data_set_name'], ccv_h['data_set_name'])
        self.assert_eq_val(resp_ccv['start_idx'], ccv_h['start_idx'])
        self.assert_eq_val(resp_ccv['end_idx'], ccv_h['end_idx'])

        # Calibration Constant info
        resp_cc = resp['data']['calibration_constant']
        self.assert_eq_val(resp_cc['name'], cc_h['name'])
        self.assert_eq_val(resp_cc['flg_available'], True)
        self.assert_eq_val(resp_cc['flg_auto_approve'], True)
        self.assert_eq_val(resp_cc['device_type_id'], -1)
        # self.assert_eq_val(resp_cc['condition_id'], -1)
        self.assert_eq_val(resp_cc['calibration_id'], -1)
        self.assert_eq_val(resp_cc['description'], cc_h['description'])

        # Physical Device info
        resp_pd = resp['data']['physical_device']
        self.assert_eq_val(resp_pd['id'], -2)
        self.assert_eq_val(resp_pd['name'], ccv_h['device_name'])
        self.assert_eq_val(resp_pd['flg_available'], True)

    def test_retrieve_calibration_constant_version(self):
        calibration_hash_01 = CalibrationTestHash(
            '2016-05-26T05:00:00.757000').valid_search_01

        cal_dict_retrieve = calibration_hash_01['karabo_h']
        det_cond_h_exp = cal_dict_retrieve['detector_condition']
        cc_h_exp = cal_dict_retrieve['calibration_constant']
        ccv_h_exp = cal_dict_retrieve['calibration_constant_version']
        #
        begin_at_exp = calibration_hash_01['begin_at_exp']
        begin_val_at_exp = calibration_hash_01['begin_validity_at_exp']
        end_val_at_exp = calibration_hash_01['end_validity_at_exp']

        # cal_name = 'CALIBRATION_TEST-2_DO_NOT_DELETE'
        cal_name = calibration_hash_01['karabo_h'][
            'calibration_constant']['calibration_name']
        # dev_name = 'PHYSICAL_DEVICE-1_DO_NOT_DELETE'
        dev_name = calibration_hash_01['karabo_h'][
            'calibration_constant_version']['device_name']

        retrieve_h = {
            'calibration_hash_schema_version': '1.0',
            'calibration_name': cal_name,
            'device_name': dev_name,
            'measured_at': begin_at_exp,  # [Default == now()]
            'snapshot_at': '',  # [Default == now()]
            'detector_condition': det_cond_h_exp
        }

        resp = CalibrationClient.retrieve_calibration_constant_version(
            self.cal_client,
            retrieve_h
        )

        # Logging information
        logging.error('calibration_hash_01: {0}'.format(calibration_hash_01))
        logging.error('retrieve_h: {0}'.format(retrieve_h))
        logging.error('resp: {0}'.format(resp))

        self.assert_eq_val(resp['success'], True)
        self.assert_eq_val(resp['app_info'], {})

        success_info_msg = 'Got calibration_constant_version successfully'
        self.assert_eq_val(resp['info'], success_info_msg)

        # Calibration Constant Version info
        resp_ccv = resp['data']

        # print('$' * 200)
        # print(str(resp_ccv))
        # print('$' * 200)
        expected_return = {
            'id': -6,
            'name': 'CALIBRATION_CONSTANT_VERSION_TEST-6_DO_NOT_DELETE',
            'file_name': 'cal.r0001.c0002.h5',
            'path_to_file': '/usr/local/cal_repo/',
            'data_set_name': 'exp001.cal001', 'flg_deployed': True,
            'flg_good_quality': True,
            'begin_validity_at': '2016-05-25T10:30:14.000+02:00',
            'end_validity_at': '2029-06-24T00:00:00.000+02:00',
            'begin_at': '2016-05-26T12:00:00.000+02:00',
            'start_idx': None,
            'end_idx': None,
            'raw_data_location': None,
            'description': None,
            'calibration_constant': {
                'id': -3,
                'name': 'CALIBRATION_CONSTANT_TEST-3_DO_NOT_DELETE',
                'flg_auto_approve': True,
                'flg_available': True,
                'description': 'Created automatically via seed:seed_tests',
                'device_type_id': -1, 'calibration_id': -2,
                'condition_id': -3},
            'physical_device': {
                'id': -1,
                'name': 'PHYSICAL_DEVICE-1_DO_NOT_DELETE',
                'device_type_id': -1, 'flg_available': True,
                'parent_id': None,
                'description': 'Created automatically via seed:seed_tests'}}

        self.assert_eq_val(resp_ccv['name'], expected_return['name'])
        self.assert_eq_val(resp_ccv['flg_good_quality'], True)

        self.assert_eq_val(resp_ccv['begin_validity_at'],
                           expected_return['begin_validity_at'])
        self.assert_eq_val(resp_ccv['end_validity_at'],
                           expected_return['end_validity_at'])
        self.assert_eq_val(resp_ccv['begin_at'], expected_return['begin_at'])

        self.assert_eq_val(resp_ccv['flg_deployed'], True)
        self.assert_eq_val(resp_ccv['raw_data_location'],
                           expected_return['raw_data_location'])
        self.assert_eq_val(resp_ccv['file_name'], expected_return['file_name'])
        self.assert_eq_val(resp_ccv['path_to_file'],
                           expected_return['path_to_file'])
        self.assert_eq_val(resp_ccv['description'],
                           expected_return['description'])
        # Special cases...
        self.assert_eq_val(resp_ccv['data_set_name'],
                           expected_return['data_set_name'])
        self.assert_eq_val(resp_ccv['start_idx'], expected_return['start_idx'])
        self.assert_eq_val(resp_ccv['end_idx'], expected_return['end_idx'])

        # Calibration Constant info
        resp_cc = resp['data']['calibration_constant']
        expected_return_cc = expected_return['calibration_constant']

        self.assert_eq_val(resp_cc['name'], expected_return_cc['name'])
        self.assert_eq_val(resp_cc['flg_available'], True)
        self.assert_eq_val(resp_cc['flg_auto_approve'], True)
        self.assert_eq_val(resp_cc['device_type_id'], -1)
        # self.assert_eq_val(resp_cc['condition_id'], -1)
        self.assert_eq_val(resp_cc['calibration_id'], -2)
        self.assert_eq_val(resp_cc['description'],
                           expected_return_cc['description'])

        # Physical Device info
        resp_pd = resp['data']['physical_device']
        expected_return_pd = expected_return['physical_device']

        self.assert_eq_val(resp_pd['id'], -1)
        self.assert_eq_val(resp_pd['name'], expected_return_pd['name'])
        self.assert_eq_val(resp_pd['flg_available'], True)

    def test_retrieve_all_calibration_constant_versions(self):
        calibration_hash_01 = CalibrationTestHash(None).valid_search_01

        cal_dict_retrieve = calibration_hash_01['karabo_h']
        det_cond_h_exp = cal_dict_retrieve['detector_condition']
        cc_h_exp = cal_dict_retrieve['calibration_constant']
        ccv_h_exp = cal_dict_retrieve['calibration_constant_version']
        #
        begin_at_exp = calibration_hash_01['begin_at_exp']
        begin_val_at_exp = calibration_hash_01['begin_validity_at_exp']
        end_val_at_exp = calibration_hash_01['end_validity_at_exp']

        # cal_name = 'CALIBRATION_TEST-2_DO_NOT_DELETE'
        cal_name = calibration_hash_01['karabo_h'][
            'calibration_constant']['calibration_name']
        # dev_name = 'PHYSICAL_DEVICE-1_DO_NOT_DELETE'
        dev_name = calibration_hash_01['karabo_h'][
            'calibration_constant_version']['device_name']

        retrieve_h = {
            'calibration_hash_schema_version': '1.0',
            'calibration_name': cal_name,
            'device_name': dev_name,
            'measured_at': begin_at_exp,  # [Default == now()]
            'snapshot_at': '',  # [Default == now()]
            'detector_condition': det_cond_h_exp
        }

        resp = CalibrationClient.retrieve_all_calibration_constant_versions(
            self.cal_client,
            retrieve_h
        )

        # Logging information
        logging.error('calibration_hash_01: {0}'.format(calibration_hash_01))
        logging.error('retrieve_h: {0}'.format(retrieve_h))
        logging.error('resp: {0}'.format(resp))

        self.assert_eq_val(resp['success'], True)
        self.assert_eq_val(resp['app_info'], {})

        success_info_msg = 'Got calibration_constant_version successfully'
        self.assert_eq_val(resp['info'], success_info_msg)

        response_data = resp['data']
        index = 0
        for ccv in response_data:
            logging.error("response.data[{0}]['id'] == {1}".format(index,
                                                                   ccv['id']))
            index += 1

        # Cannot test this because new data is being added on the other tests!
        # self.assert_eq_val(len(response_data), 2)

        # Calibration Constant Version info (position 0)
        resp_ccv_0 = response_data[0]

        self.assert_eq_val(resp_ccv_0['name'], self.existing_db_06['name'])
        self.assert_eq_val(resp_ccv_0['flg_good_quality'],
                           self.existing_db_06['flg_good_quality'])

        self.assert_eq_val(resp_ccv_0['begin_validity_at'],
                           self.existing_db_06['begin_validity_at'])
        self.assert_eq_val(resp_ccv_0['end_validity_at'],
                           self.existing_db_06['end_validity_at'])
        self.assert_eq_val(resp_ccv_0['begin_at'],
                           self.existing_db_06['begin_at'])

        self.assert_eq_val(resp_ccv_0['flg_deployed'],
                           self.existing_db_06['flg_deployed'])
        self.assert_eq_val(resp_ccv_0['raw_data_location'],
                           self.existing_db_06['raw_data_location'])
        self.assert_eq_val(resp_ccv_0['file_name'],
                           self.existing_db_06['file_name'])
        self.assert_eq_val(resp_ccv_0['path_to_file'],
                           self.existing_db_06['path_to_file'])
        self.assert_eq_val(resp_ccv_0['description'],
                           self.existing_db_06['description'])
        # Special cases...
        self.assert_eq_val(resp_ccv_0['data_set_name'],
                           self.existing_db_06['data_set_name'])
        self.assert_eq_val(resp_ccv_0['start_idx'],
                           self.existing_db_06['start_idx'])
        self.assert_eq_val(resp_ccv_0['end_idx'],
                           self.existing_db_06['end_idx'])

        # Calibration Constant info
        self.assert_eq_val(resp_ccv_0['calibration_constant']['id'],
                           self.existing_db_06['calibration_constant_id'])

        # Physical Device info
        self.assert_eq_val(resp_ccv_0['physical_device']['id'],
                           self.existing_db_06['physical_device_id'])

        #
        # Calibration Constant Version info (position 1)
        resp_ccv_1 = response_data[1]

        self.assert_eq_val(resp_ccv_1['name'], self.existing_db_05['name'])
        self.assert_eq_val(resp_ccv_1['flg_good_quality'],
                           self.existing_db_05['flg_good_quality'])

        self.assert_eq_val(resp_ccv_1['begin_validity_at'],
                           self.existing_db_05['begin_validity_at'])
        self.assert_eq_val(resp_ccv_1['end_validity_at'],
                           self.existing_db_05['end_validity_at'])
        self.assert_eq_val(resp_ccv_1['begin_at'],
                           self.existing_db_05['begin_at'])

        self.assert_eq_val(resp_ccv_1['flg_deployed'],
                           self.existing_db_05['flg_deployed'])
        self.assert_eq_val(resp_ccv_1['raw_data_location'],
                           self.existing_db_05['raw_data_location'])
        self.assert_eq_val(resp_ccv_1['file_name'],
                           self.existing_db_05['file_name'])
        self.assert_eq_val(resp_ccv_1['path_to_file'],
                           self.existing_db_05['path_to_file'])
        self.assert_eq_val(resp_ccv_1['description'],
                           self.existing_db_05['description'])
        # Special cases...
        self.assert_eq_val(resp_ccv_1['data_set_name'],
                           self.existing_db_05['data_set_name'])
        self.assert_eq_val(resp_ccv_1['start_idx'],
                           self.existing_db_05['start_idx'])
        self.assert_eq_val(resp_ccv_1['end_idx'],
                           self.existing_db_05['end_idx'])

        # Calibration Constant info
        self.assert_eq_val(resp_ccv_1['calibration_constant']['id'],
                           self.existing_db_05['calibration_constant_id'])

        # Physical Device info
        self.assert_eq_val(resp_ccv_1['physical_device']['id'],
                           self.existing_db_05['physical_device_id'])

    def test_retrieve_ccv_no_data_found(self):
        calibration_hash_01 = CalibrationTestHash(None).valid_search_01

        cal_dict_retrieve = calibration_hash_01['karabo_h']
        det_cond_h_exp = cal_dict_retrieve['detector_condition']
        cc_h_exp = cal_dict_retrieve['calibration_constant']
        ccv_h_exp = cal_dict_retrieve['calibration_constant_version']
        #
        begin_at_exp = calibration_hash_01['begin_at_exp']
        begin_val_at_exp = calibration_hash_01['begin_validity_at_exp']
        end_val_at_exp = calibration_hash_01['end_validity_at_exp']

        # cal_name = 'CALIBRATION_TEST-2_DO_NOT_DELETE'
        cal_name = calibration_hash_01['karabo_h'][
            'calibration_constant']['calibration_name']
        dev_name = 'PHYSICAL_DEVICE-3_DO_NOT_DELETE'
        # dev_name = calibration_hash_01['karabo_h'][
        #     'calibration_constant_version']['device_name']

        retrieve_h = {
            'calibration_hash_schema_version': '1.0',
            'calibration_name': cal_name,
            'device_name': dev_name,
            # ==================>>>
            # ERROR IS HERE:
            # Because end_validity_at was set to 1 second after the begin_at
            # and when this test is run, more than 1 second has passed
            'measured_at': '',  # [Default == now()]
            # <<<==================
            'snapshot_at': '',  # [Default == now()]
            'detector_condition': det_cond_h_exp
        }

        resp = CalibrationClient.retrieve_calibration_constant_version(
            self.cal_client,
            retrieve_h
        )

        # Logging information
        logging.error('calibration_hash_01: {0}'.format(calibration_hash_01))
        logging.error('retrieve_h: {0}'.format(retrieve_h))
        logging.error('resp: {0}'.format(resp))

        self.assert_eq_val(resp['success'], False)
        self.assert_eq_val(resp['app_info'], RESOURCE_NOT_FOUND)
        self.assert_eq_val(resp['data'], {})

        extra_info = 'calibration_constant_version not found!'
        self.assert_eq_val(resp['info'], extra_info)

    def test_create_condition_from_dict_success(self):
        __parameters_01 = [
            {
                # 'parameter_id': '-1',
                'parameter_name': 'PARAMETER_TEST-1_DO_NOT_DELETE',
                'value': '2.5',
                'lower_deviation_value': '0.5',
                'upper_deviation_value': '0.5',
                'flg_available': 'true',
                'description': 'Created automatically via seed:seed_tests'
            },
            {
                # 'parameter_id': '-2',
                'parameter_name': 'PARAMETER_TEST-2_DO_NOT_DELETE',
                'value': '1.5',
                'lower_deviation_value': '0.5',
                'upper_deviation_value': '0.5',
                'flg_available': 'true',
                'description': 'Created automatically via seed:seed_tests'
            }
        ]

        __unique_name = 'CONDITION_TEST-1_DO_NOT_DELETE'

        cond_dict = {
            'name': __unique_name,
            'flg_available': 'true',
            'description': 'Created automatically via seed:seed_tests',
            'parameters': __parameters_01
        }

        #
        # Set Condition from DICT (should succeed with existent)
        #
        resp = CalibrationClient.set_condition_from_dict(self.cal_client,
                                                         cond_dict)

        expect = {'id': -1,
                  'flg_available': True,
                  'name': 'CONDITION_TEST-1_DO_NOT_DELETE',
                  'description': 'Created automatically via seed:seed_tests',
                  'num_parameters': 2}

        msg = 'Got {0} successfully'.format(CONDITION)
        expect = {'success': True, 'info': msg, 'app_info': {}, 'data': expect}

        self.assert_eq_val(resp['app_info'], {})
        self.assert_eq_val(resp['info'], expect['info'])
        self.assert_eq_val(resp['success'], expect['success'])

        # Validate all 'data' fields
        expect_data = expect['data']
        if type(expect_data) is dict and len(expect_data) > 0:
            for key, val in expect_data.items():
                self.assert_eq_val(resp['data'][key], expect_data[key])
        else:
            self.assert_eq_val(resp['data'], expect_data)

    def test_create_condition_from_dict_error(self):
        __parameters_01 = [
            {
                # 'parameter_id': '-1',
                'parameter_name': 'PARAMETER_TEST-1_DO_NOT_DELETE',
                'value': '100.5',
                'lower_deviation_value': '10.5',
                'upper_deviation_value': '10.5',
                'flg_available': 'true',
                'description': 'Created automatically via seed:seed_tests'
            }
        ]

        __unique_name = 'CONDITION_TEST-1_DO_NOT_DELETE'

        expect = {
            'name': __unique_name,
            'flg_available': 'true',
            'description': 'Created automatically via seed:seed_tests',
            'parameters': __parameters_01
        }

        #
        # Set Condition from DICT (should succeed with existent)
        #
        resp = CalibrationClient.set_condition_from_dict(self.cal_client,
                                                         expect)

        expect_app_info = {'name': ['has already been taken']}
        self.assert_find_error(CONDITION, resp, expect_app_info)

    def test_update_calibration_constant_version(self):

        # should succeed
        update_h = {
            'ccv_id': -1,
            'flg_good_quality': True,
            'description': 'bla',
            'end_idx': 0,
            'start_idx': 0,
            'flg_deployed': False
        }

        resp = CalibrationClient.update_calibration_constant_version(
            self.cal_client,
            update_h
        )

        # Logging information
        logging.error('update_h: {0}'.format(update_h))
        logging.error('resp: {0}'.format(resp))

        self.assert_eq_val(resp['success'], True)
        self.assert_eq_val(resp['app_info'], {})

        success_info_msg = 'calibration_constant_version updated successfully'
        self.assert_eq_val(resp['info'], success_info_msg)

        # Calibration Constant Version info
        resp_ccv = resp['data']
        self.assert_eq_val(resp_ccv['flg_good_quality'],
                           update_h['flg_good_quality'])
        self.assert_eq_val(resp_ccv['description'], update_h['description'])
        self.assert_eq_val(resp_ccv['end_idx'], update_h['end_idx'])
        self.assert_eq_val(resp_ccv['start_idx'], update_h['start_idx'])
        self.assert_eq_val(resp_ccv['flg_deployed'], update_h['flg_deployed'])

        # Update information back
        update_back_h = {
            'ccv_id': -1,
            'flg_good_quality': True,
            'description': None,
            'end_idx': None,
            'start_idx': None,
            'flg_deployed': True
        }

        resp = CalibrationClient.update_calibration_constant_version(
            self.cal_client,
            update_back_h
        )

        self.assert_eq_val(resp['success'], True)
        self.assert_eq_val(resp['app_info'], {})

        success_info_msg = 'calibration_constant_version updated successfully'
        self.assert_eq_val(resp['info'], success_info_msg)

        # Calibration Constant Version info
        resp_ccv = resp['data']
        self.assert_eq_val(resp_ccv['description'],
                           update_back_h['description'])
        self.assert_eq_val(resp_ccv['end_idx'], update_back_h['end_idx'])
        self.assert_eq_val(resp_ccv['start_idx'], update_back_h['start_idx'])
        self.assert_eq_val(resp_ccv['flg_deployed'],
                           update_back_h['flg_deployed'])

        # should fail
        update_h_failed = {'ccv_id': -100}
        resp_failed = CalibrationClient.update_calibration_constant_version(
            self.cal_client,
            update_h_failed
        )

        # Logging information
        logging.error('update_h_failed: {0}'.format(update_h_failed))
        logging.error('resp_failed: {0}'.format(resp_failed))

        self.assert_eq_val(resp_failed['success'], False)
        self.assert_eq_val(resp_failed['app_info'], 'Resource not found!')

        success_info_msg = 'calibration_constant_version not found!'
        self.assert_eq_val(resp_failed['info'], success_info_msg)


if __name__ == '__main__':
    unittest.main()
