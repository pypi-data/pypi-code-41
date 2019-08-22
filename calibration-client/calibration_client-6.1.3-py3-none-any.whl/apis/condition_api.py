"""ConditionApi module class"""

import json

from ..common.base import Base


class ConditionApi(Base):
    def get_possible_conditions(self, condition):
        api_url = self.__get_api_url('get_possible_conditions')

        self.check_session_token()
        return self.oauth_client.session.get(api_url,
                                             data=json.dumps(condition),
                                             headers=self.headers)

    def get_expected_condition(self, condition):
        api_url = self.__get_api_url('get_expected_condition')

        self.check_session_token()
        return self.oauth_client.session.get(api_url,
                                             data=json.dumps(condition),
                                             headers=self.headers)

    def set_expected_condition(self, condition):
        api_url = self.__get_api_url('set_expected_condition')

        self.check_session_token()
        return self.oauth_client.session.post(api_url,
                                              data=json.dumps(condition),
                                              headers=self.headers)

    #
    # Private Methods
    #
    def __get_api_url(self, api_specifics=''):
        model_name = 'conditions/'
        return self.get_api_url(model_name, api_specifics)
