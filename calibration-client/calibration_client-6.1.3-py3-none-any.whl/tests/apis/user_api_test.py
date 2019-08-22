"""UserApiTest class"""

import unittest

from .api_base import ApiBase
from ..common.config_test import *
from ..common.secrets import *
from ...calibration_client_api import CalibrationClientApi


class UserApiTest(ApiBase, unittest.TestCase):
    cal_client_api = CalibrationClientApi(
        client_id=CLIENT_OAUTH2_INFO['CLIENT_ID'],
        client_secret=CLIENT_OAUTH2_INFO['CLIENT_SECRET'],
        token_url=CLIENT_OAUTH2_INFO['TOKEN_URL'],
        refresh_url=CLIENT_OAUTH2_INFO['REFRESH_URL'],
        auth_url=CLIENT_OAUTH2_INFO['AUTH_URL'],
        scope=CLIENT_OAUTH2_INFO['SCOPE'],
        user_email=CLIENT_OAUTH2_INFO['EMAIL'],
        base_api_url=BASE_API_URL)

    __current_user_info_01 = {
        u'email': str(CLIENT_OAUTH2_INFO['EMAIL']),
        u'first_name': str(CLIENT_OAUTH2_INFO['first_name']),
        u'last_name': str(CLIENT_OAUTH2_INFO['last_name']),
        u'name': str(CLIENT_OAUTH2_INFO['name']),
        u'nickname': str(CLIENT_OAUTH2_INFO['nickname']),
        u'provider': str(CLIENT_OAUTH2_INFO['provider']),
        u'uid': str(CLIENT_OAUTH2_INFO['uid'])
    }

    def test_user_info(self):
        current_user = self.__current_user_info_01

        resp = self.cal_client_api.get_current_user()
        resp_content = self.load_response_content(resp)

        # Debug Response
        # self.debug_response(response)

        receive = resp_content
        expect = current_user
        #
        self.fields_validation(receive, expect)
        self.assert_eq_status_code(resp.status_code, OK)

    #
    # fields_validation
    #
    def fields_validation(self, receive, expect):
        self.assert_eq_hfield(receive, expect, 'email', STRING)
        self.assert_eq_hfield(receive, expect, 'first_name', STRING)
        self.assert_eq_hfield(receive, expect, 'last_name', STRING)
        self.assert_eq_hfield(receive, expect, 'name', STRING)
        self.assert_eq_hfield(receive, expect, 'nickname', STRING)
        self.assert_eq_hfield(receive, expect, 'provider', STRING)
        self.assert_eq_hfield(receive, expect, 'uid', STRING)


if __name__ == '__main__':
    unittest.main()
