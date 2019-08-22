"""DeviceType module class"""

from ..apis.device_type_api import DeviceTypeApi
from ..common.base import Base
from ..common.config import *

MODULE_NAME = DEVICE_TYPE


class DeviceType(DeviceTypeApi):
    def __init__(self, calibration_client,
                 name, flg_available, description=''):
        self.calibration_client = calibration_client
        self.id = None
        self.name = name
        self.flg_available = flg_available
        self.description = description

    def create(self):
        cal_client = self.calibration_client
        response = cal_client.create_device_type_api(self.__get_resource())

        Base.cal_debug(MODULE_NAME, CREATE, response)
        res = Base.format_response(response, CREATE, CREATED, MODULE_NAME)

        if res['success']:
            self.id = res['data']['id']

        return res

    def delete(self):
        cal_client = self.calibration_client
        response = cal_client.delete_device_type_api(self.id)
        Base.cal_debug(MODULE_NAME, DELETE, response)

        return Base.format_response(response, DELETE, NO_CONTENT, MODULE_NAME)

    def update(self):
        cal_client = self.calibration_client
        response = cal_client.update_device_type_api(self.id,
                                                     self.__get_resource())

        Base.cal_debug(MODULE_NAME, UPDATE, response)
        return Base.format_response(response, UPDATE, OK, MODULE_NAME)

    @staticmethod
    def get_by_id(cal_client, device_type_id):
        response = cal_client.get_device_type_by_id_api(device_type_id)

        Base.cal_debug(MODULE_NAME, 'get_by_id', response)
        return Base.format_response(response, GET, OK, MODULE_NAME)

    @staticmethod
    def get_all_by_name(cal_client, name):
        response = cal_client.get_all_device_types_by_name_api(name)

        Base.cal_debug(MODULE_NAME, 'get_all_by_name', response)
        return Base.format_response(response, GET, OK, MODULE_NAME)

    @staticmethod
    def get_by_name(cal_client, name):
        res = DeviceType.get_all_by_name(cal_client, name)

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
        device_type = {
            DEVICE_TYPE: {
                'name': self.name,
                'flg_available': self.flg_available,
                'description': self.description
            }
        }

        return device_type
