"""DeviceTypeApi module class"""

import json

from ..common.base import Base


class DeviceTypeApi(Base):
    def create_device_type_api(self, parameter):
        api_url = self.__get_api_url()
        return self.api_post(api_url, data=json.dumps(parameter))

    def delete_device_type_api(self, parameter_id):
        api_url = self.__get_api_url(parameter_id)
        return self.api_delete(api_url)

    def update_device_type_api(self, device_type_id, device_type):
        api_url = self.__get_api_url(device_type_id)
        return self.api_put(api_url, data=json.dumps(device_type))

    def get_device_type_by_id_api(self, parameter_id):
        api_url = self.__get_api_url(parameter_id)
        return self.api_get(api_url, params={})

    def get_all_device_types_by_name_api(self, name):
        api_url = self.__get_api_url()
        return self.api_get(api_url, params={'name': name})

    #
    # Private Methods
    #
    def __get_api_url(self, api_specifics=''):
        model_name = 'device_types/'
        return self.get_api_url(model_name, api_specifics)
