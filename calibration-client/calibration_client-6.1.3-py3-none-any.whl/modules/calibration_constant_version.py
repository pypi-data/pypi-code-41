"""CalibrationConstantVersion module class"""

from ..apis.calibration_constant_version_api import \
    CalibrationConstantVersionApi
from ..common.base import Base
from ..common.config import *

MODULE_NAME = CALIBRATION_CONSTANT_VERSION


class CalibrationConstantVersion(CalibrationConstantVersionApi):
    def __init__(self, calibration_client,
                 name, file_name, path_to_file, data_set_name,
                 calibration_constant_id, physical_device_id,
                 flg_deployed, flg_good_quality,
                 begin_validity_at, end_validity_at, begin_at,
                 start_idx, end_idx, raw_data_location,
                 description=''):
        self.calibration_client = calibration_client
        self.id = None
        self.name = name
        self.file_name = file_name
        self.path_to_file = path_to_file
        self.data_set_name = data_set_name
        self.calibration_constant_id = calibration_constant_id
        self.physical_device_id = physical_device_id
        self.flg_deployed = flg_deployed
        self.flg_good_quality = flg_good_quality
        self.begin_validity_at = begin_validity_at
        self.end_validity_at = end_validity_at
        self.begin_at = begin_at
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.raw_data_location = raw_data_location
        self.description = description

    def create(self):
        cal_client = self.calibration_client
        resp = cal_client.create_calibration_constant_version_api(
            self.__get_resource())

        Base.cal_debug(MODULE_NAME, CREATE, resp)
        res = Base.format_response(resp, CREATE, CREATED, MODULE_NAME)

        if res['success']:
            self.id = res['data']['id']

        return res

    #
    # Delete CalibrationConstantVersion instances is not allowed by the server,
    # and consequently this action isn't provided to the user!
    #
    # def delete(self):
    #     cal_client = self.calibration_client
    #     resp = cal_client.delete_calibration_constant_version_api(self.id)
    #     Base.cal_debug(MODULE_NAME, DELETE, resp)
    #     return Base.format_response(resp, DELETE, NO_CONTENT, MODULE_NAME)

    def update(self):
        cal_client = self.calibration_client
        resp = cal_client.update_calibration_constant_version_api(
            self.id,
            self.__get_resource()
        )

        Base.cal_debug(MODULE_NAME, UPDATE, resp)
        return Base.format_response(resp, UPDATE, OK, MODULE_NAME)

    @staticmethod
    def create_from_dict(cal_client, ccv):
        new_ccv = CalibrationConstantVersion(
            calibration_client=cal_client,
            name=ccv['name'],
            file_name=ccv['file_name'],
            path_to_file=ccv['path_to_file'],
            data_set_name=ccv['data_set_name'],
            calibration_constant_id=ccv['calibration_constant_id'],
            physical_device_id=ccv['physical_device_id'],
            flg_deployed=ccv['flg_deployed'],
            flg_good_quality=ccv['flg_good_quality'],
            begin_validity_at=ccv['begin_validity_at'],
            end_validity_at=ccv['end_validity_at'],
            begin_at=ccv['begin_at'],
            start_idx=ccv['start_idx'],
            end_idx=ccv['end_idx'],
            raw_data_location=ccv['raw_data_location'],
            description=ccv['description'])

        resp = new_ccv.create()
        return resp

    @staticmethod
    def get_by_id(cal_client, ccv_id):
        resp = cal_client.get_calibration_constant_version_by_id_api(ccv_id)

        Base.cal_debug(MODULE_NAME, 'get_by_id', resp)
        return Base.format_response(resp, GET, OK, MODULE_NAME)

    @staticmethod
    def get_all_by_name(cal_client, name):
        resp = cal_client.get_all_calibration_constant_versions_by_name_api(
            name
        )

        Base.cal_debug(MODULE_NAME, 'get_all_by_name', resp)
        return Base.format_response(resp, GET, OK, MODULE_NAME)

    @staticmethod
    def get_by_name(cal_client, name):
        resp = CalibrationConstantVersion.get_all_by_name(cal_client, name)

        if resp['success']:
            if resp['data'] == []:
                resp_data = []
            else:
                resp_data = resp['data'][0]

            resp = {'success': resp['success'],
                    'info': resp['info'],
                    'app_info': resp['app_info'],
                    'data': resp_data}

        return resp

    # Returns the CCV (of one CC) which the provided event_at is between
    # the CCV.begin_at and CCV.end_at
    @staticmethod
    def get_by_uk(cal_client,
                  calibration_constant_id, physical_device_id,
                  event_at, snapshot_at):
        resp = cal_client.get_calibration_constant_version_by_uk_api(
            calibration_constant_id, physical_device_id,
            event_at, snapshot_at
        )

        Base.cal_debug(MODULE_NAME, 'ccv >> get_by_uk', resp)
        return Base.format_response(resp, GET, OK, MODULE_NAME)

    # Returns the CCV (of several CCs) with closest relation between the
    # provided event_at and the CCV.begin_at
    @staticmethod
    def get_closest_by_time(cal_client,
                            calibration_constant_ids, physical_device_id,
                            event_at, snapshot_at):
        resp = cal_client.get_closest_calibration_constant_version_api(
            calibration_constant_ids, physical_device_id,
            event_at, snapshot_at
        )

        Base.cal_debug(MODULE_NAME,
                       'ccv >> get_closest_calibration_constant_version_api',
                       resp)
        return Base.format_response(resp, GET, OK, MODULE_NAME)

    # To return all constant versions
    @staticmethod
    def get_all_versions(cal_client,
                         calibration_constant_ids, physical_device_id,
                         event_at, snapshot_at):

        resp = cal_client.get_all_calibration_constant_versions_api(
            calibration_constant_ids, physical_device_id,
            event_at, snapshot_at
        )

        Base.cal_debug(MODULE_NAME,
                       'ccv >> get_all_calibration_constant_versions_api',
                       resp)
        return Base.format_response(resp, GET, OK, MODULE_NAME)

    def __get_resource(self):
        calibration_constant_version = {
            CALIBRATION_CONSTANT_VERSION: {
                'name': self.name,
                'file_name': self.file_name,
                'path_to_file': self.path_to_file,
                'data_set_name': self.data_set_name,
                'calibration_constant_id': self.calibration_constant_id,
                'physical_device_id': self.physical_device_id,
                'flg_deployed': self.flg_deployed,
                'flg_good_quality': self.flg_good_quality,
                'begin_validity_at': self.begin_validity_at,
                'end_validity_at': self.end_validity_at,
                'begin_at': self.begin_at,
                'start_idx': self.start_idx,
                'end_idx': self.end_idx,
                'raw_data_location': self.raw_data_location,
                'description': self.description
            }
        }

        return calibration_constant_version
