"""ConditionApiTest class"""

import unittest

from .api_base import ApiBase
from ..common.config_test import *
from ..common.secrets import *
from ...calibration_client_api import CalibrationClientApi


class ConditionApiTest(ApiBase, unittest.TestCase):
    cal_client_api = CalibrationClientApi(
        client_id=CLIENT_OAUTH2_INFO['CLIENT_ID'],
        client_secret=CLIENT_OAUTH2_INFO['CLIENT_SECRET'],
        token_url=CLIENT_OAUTH2_INFO['TOKEN_URL'],
        refresh_url=CLIENT_OAUTH2_INFO['REFRESH_URL'],
        auth_url=CLIENT_OAUTH2_INFO['AUTH_URL'],
        scope=CLIENT_OAUTH2_INFO['SCOPE'],
        user_email=CLIENT_OAUTH2_INFO['EMAIL'],
        base_api_url=BASE_API_URL)

    __unique_name = 'CONDITION_TEST-1_DO_NOT_DELETE'

    def test_expected_condition(self):
        parameters_conditions_attr = [
            {
                'parameter_id': '-1',
                'value': '2.5',
                'lower_deviation_value': '0.5',
                'upper_deviation_value': '0.5',
                'flg_available': 'true',
                'description': 'Created automatically via seed:seed_tests'
            },
            {
                'parameter_id': '-2',
                'value': '1.5',
                'lower_deviation_value': '0.5',
                'upper_deviation_value': '0.5',
                'flg_available': 'true',
                'description': 'Created automatically via seed:seed_tests'
            }
        ]

        condition = {
            'condition': {
                'name': self.__unique_name,
                'flg_available': 'true',
                'description': 'Created automatically via seed:seed_tests',
                'parameters_conditions_attributes': parameters_conditions_attr
            }
        }

        expect = condition['condition']
        # expect_params_conditions = len(parameters_conditions_attr)

        response1 = self.cal_client_api.set_expected_condition(condition)
        resp_content = self.load_response_content(response1)
        receive = resp_content

        #
        # This test cannot be done because this function can return
        # either one of the following messages:
        # 1) self.assert_eq_str(response_content['info'],
        #   'Condition was successfully created.')
        # 2) self.assert_eq_str(response_content['info'],
        #   'Condition was successfully found.')
        self.fields_validation(receive, expect)
        # self.assert_eq_status_code(response1.status_code, CREATED)
        self.assert_eq_status_code(response1.status_code, OK)

        response2 = self.cal_client_api.get_expected_condition(condition)
        resp_content = self.load_response_content(response2)
        receive = resp_content

        self.fields_validation(receive, expect)
        self.assert_eq_status_code(response2.status_code, OK)

    def test_possible_conditions_exact_values(self):
        cal_client = CalibrationClientApi(
            client_id=CLIENT_OAUTH2_INFO['CLIENT_ID'],
            client_secret=CLIENT_OAUTH2_INFO['CLIENT_SECRET'],
            token_url=CLIENT_OAUTH2_INFO['TOKEN_URL'],
            refresh_url=CLIENT_OAUTH2_INFO['REFRESH_URL'],
            auth_url=CLIENT_OAUTH2_INFO['AUTH_URL'],
            scope=CLIENT_OAUTH2_INFO['SCOPE'],
            user_email=CLIENT_OAUTH2_INFO['EMAIL'],
            base_api_url=BASE_API_URL)

        parameters_conditions_attr = [
            {
                'parameter_id': '-1',
                'value': '2.5',
                'lower_deviation_value': '0.5',
                'upper_deviation_value': '0.5',
                'flg_available': 'true',
                'description': 'Created automatically via seed:seed_tests'
            },
            {
                'parameter_id': '-2',
                'value': '1.5',
                'lower_deviation_value': '0.5',
                'upper_deviation_value': '0.5',
                'flg_available': 'true',
                'description': 'Created automatically via seed:seed_tests'
            }
        ]

        condition = {
            'condition': {
                'name': self.__unique_name,
                'event_at': '2019-07-25 09:14:52',
                'flg_available': 'true',
                'description': 'Created automatically via seed:seed_tests',
                'parameters_conditions_attributes': parameters_conditions_attr
            }
        }

        expect = condition['condition']
        expect_params_conditions = len(parameters_conditions_attr)

        response = cal_client.get_possible_conditions(condition)
        resp_content = self.load_response_content(response)
        receive = resp_content[0]

        self.assert_eq_status_code(response.status_code, OK)
        self.fields_validation(receive, expect)

    def test_possible_conditions_near_values(self):
        cal_client = CalibrationClientApi(
            client_id=CLIENT_OAUTH2_INFO['CLIENT_ID'],
            client_secret=CLIENT_OAUTH2_INFO['CLIENT_SECRET'],
            token_url=CLIENT_OAUTH2_INFO['TOKEN_URL'],
            refresh_url=CLIENT_OAUTH2_INFO['REFRESH_URL'],
            auth_url=CLIENT_OAUTH2_INFO['AUTH_URL'],
            scope=CLIENT_OAUTH2_INFO['SCOPE'],
            user_email=CLIENT_OAUTH2_INFO['EMAIL'],
            base_api_url=BASE_API_URL)

        parameters_conditions_attr = [
            {
                'parameter_id': '-1',
                'value': '2.0',
                'lower_deviation_value': '0.5',
                'upper_deviation_value': '0.5',
                'flg_available': 'true',
                'description': 'Created automatically via seed:seed_tests'
            },
            {
                'parameter_id': '-2',
                'value': '1.999',
                'lower_deviation_value': '0.5',
                'upper_deviation_value': '0.5',
                'flg_available': 'true',
                'description': 'Created automatically via seed:seed_tests'
            }
        ]

        condition = {
            'condition': {
                'name': self.__unique_name,
                'flg_available': 'true',
                'description': 'Created automatically via seed:seed_tests',
                'parameters_conditions_attributes': parameters_conditions_attr
            }
        }

        expect = condition['condition']
        # expect_params_conditions = len(parameters_conditions_attr)

        response = cal_client.get_possible_conditions(condition)
        resp_content = self.load_response_content(response)
        receive = resp_content[0]

        self.fields_validation(receive, expect)
        self.assert_eq_status_code(response.status_code, OK)

    def test_possible_conditions_outside_values(self):
        cal_client = CalibrationClientApi(
            client_id=CLIENT_OAUTH2_INFO['CLIENT_ID'],
            client_secret=CLIENT_OAUTH2_INFO['CLIENT_SECRET'],
            token_url=CLIENT_OAUTH2_INFO['TOKEN_URL'],
            refresh_url=CLIENT_OAUTH2_INFO['REFRESH_URL'],
            auth_url=CLIENT_OAUTH2_INFO['AUTH_URL'],
            scope=CLIENT_OAUTH2_INFO['SCOPE'],
            user_email=CLIENT_OAUTH2_INFO['EMAIL'],
            base_api_url=BASE_API_URL)

        parameters_conditions_attr = [
            {
                'parameter_id': '-1',
                'value': '2.0',
                'lower_deviation_value': '0.5',
                'upper_deviation_value': '0.5',
                'flg_available': 'true',
                'description': 'Created automatically via seed:seed_tests'
            },
            {
                'parameter_id': '-2',
                'value': '2.000001',  # Value outside bunderies
                'lower_deviation_value': '0.5',
                'upper_deviation_value': '0.5',
                'flg_available': 'true',
                'description': 'Created automatically via seed:seed_tests'
            }
        ]

        condition = {
            'condition': {
                'name': self.__unique_name,
                'flg_available': 'true',
                'description': '',
                'parameters_conditions_attributes': parameters_conditions_attr
            }
        }

        response = cal_client.get_possible_conditions(condition)
        resp_content = self.load_response_content(response)

        receive = resp_content
        receive_msg = receive['info']
        expect_msg = RESOURCE_NOT_FOUND
        expect = {'info': expect_msg}

        self.assertEqual(receive, expect, "Data must not be found")
        self.assert_eq_status_code(response.status_code, NOT_FOUND)
        self.assert_eq_str(receive_msg, expect_msg)

    #
    # fields_validation
    #
    def fields_validation(self, receive, expect):
        self.assert_eq_hfield(receive, expect, 'name', STRING)
        self.assert_eq_hfield(receive, expect, 'flg_available', BOOLEAN)
        self.assert_eq_hfield(receive, expect, 'description', STRING)

        num_params = len(expect['parameters_conditions_attributes'])
        num_params_h = {'num_parameters': num_params}
        self.assert_eq_hfield(receive, num_params_h, 'num_parameters', NUMBER)


if __name__ == '__main__':
    unittest.main()
