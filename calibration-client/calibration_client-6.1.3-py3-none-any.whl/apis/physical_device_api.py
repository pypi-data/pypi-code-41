"""PhysicalDeviceApi module class"""

import json

from ..common.base import Base


class PhysicalDeviceApi(Base):
    def create_physical_device_api(self, physical_device):
        api_url = self.__get_api_url()
        return self.api_post(api_url, data=json.dumps(physical_device))

    def delete_physical_device_api(self, physical_device_id):
        api_url = self.__get_api_url(physical_device_id)
        return self.api_delete(api_url)

    def update_physical_device_api(self, physical_device_id, physical_device):
        api_url = self.__get_api_url(physical_device_id)
        return self.api_put(api_url, data=json.dumps(physical_device))

    def get_physical_device_by_id_api(self, physical_device_id):
        api_url = self.__get_api_url(physical_device_id)
        return self.api_get(api_url, params={})

    def get_all_physical_devices_by_name_api(self, name):
        api_url = self.__get_api_url()
        return self.api_get(api_url, params={'name': name})

    #
    # Private Methods
    #
    def __get_api_url(self, api_specifics=''):
        model_name = 'physical_devices/'
        return self.get_api_url(model_name, api_specifics)
