"""CalibrationConstantVersionApi class"""

import json

from ..common.base import Base


class CalibrationConstantVersionApi(Base):
    def create_calibration_constant_version_api(self, ccv):
        api_url = self.__get_api_url()
        return self.api_post(api_url, data=json.dumps(ccv))

    #
    # Delete CalibrationConstantVersion instances is not allowed by the server,
    # and consequently this action isn't provided to the user!
    #
    # def delete_calibration_constant_version_api(self, ccv_id):
    #     api_url = self.__get_api_url(ccv_id)
    #     return self.api_delete(api_url)

    def update_calibration_constant_version_api(self, ccv_id, ccv):
        api_url = self.__get_api_url(ccv_id)
        return self.api_put(api_url, data=json.dumps(ccv))

    def get_calibration_constant_version_by_id_api(self, ccv_id):
        api_url = self.__get_api_url(ccv_id)
        return self.api_get(api_url, params={})

    def get_all_calibration_constant_versions_by_name_api(self, name):
        api_url = self.__get_api_url()
        return self.api_get(api_url, params={'name': name})

    #
    # Private Methods
    #
    def __get_api_url(self, api_specifics=''):
        model_name = 'calibration_constant_versions/'
        return self.get_api_url(model_name, api_specifics)
