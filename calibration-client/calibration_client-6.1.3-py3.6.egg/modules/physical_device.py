"""PhysicalDevice module class"""

from ..apis.physical_device_api import PhysicalDeviceApi
from ..common.base import Base
from ..common.config import *

MODULE_NAME = PHYSICAL_DEVICE


class PhysicalDevice(PhysicalDeviceApi):
    def __init__(self, calibration_client,
                 name, device_type_id, flg_available,
                 parent_id=None, description=''):
        self.calibration_client = calibration_client
        self.id = None
        self.name = name
        self.device_type_id = device_type_id
        self.flg_available = flg_available
        self.parent_id = parent_id
        self.description = description

    def create(self):
        cal_client = self.calibration_client
        response = cal_client.create_physical_device_api(self.__get_resource())

        Base.cal_debug(MODULE_NAME, CREATE, response)
        res = Base.format_response(response, CREATE, CREATED, MODULE_NAME)

        if res['success']:
            self.id = res['data']['id']

        return res

    def delete(self):
        cal_client = self.calibration_client
        response = cal_client.delete_physical_device_api(self.id)

        Base.cal_debug(MODULE_NAME, DELETE, response)
        return Base.format_response(response, DELETE, NO_CONTENT, MODULE_NAME)

    def update(self):
        cal_client = self.calibration_client
        response = cal_client.update_physical_device_api(self.id,
                                                         self.__get_resource())

        Base.cal_debug(MODULE_NAME, UPDATE, response)
        return Base.format_response(response, UPDATE, OK, MODULE_NAME)

    @staticmethod
    def get_by_id(cal_client, physical_device_id):
        response = cal_client.get_physical_device_by_id_api(physical_device_id)

        Base.cal_debug(MODULE_NAME, 'get_by_id', response)
        return Base.format_response(response, GET, OK, MODULE_NAME)

    @staticmethod
    def get_all_by_name(cal_client, name):
        response = cal_client.get_all_physical_devices_by_name_api(name)

        Base.cal_debug(MODULE_NAME, 'get_all_by_name', response)
        return Base.format_response(response, GET, OK, MODULE_NAME)

    @staticmethod
    def get_by_name(cal_client, name):
        res = PhysicalDevice.get_all_by_name(cal_client, name)

        if res['success']:
            if res['data'] == []:
                resp_data = []
            else:
                resp_data = res['data'][0]

            res = {'success': res['success'],
                   'info': res['info'],
                   'app_info': res['app_info'],
                   'data': resp_data}

        return res

    def __get_resource(self):
        physical_device = {
            PHYSICAL_DEVICE: {
                'name': self.name,
                'device_type_id': self.device_type_id,
                'flg_available': self.flg_available,
                'parent_id': self.parent_id,
                'description': self.description
            }
        }

        return physical_device
