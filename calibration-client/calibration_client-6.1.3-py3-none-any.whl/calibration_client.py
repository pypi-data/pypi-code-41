"""CalibrationClient class"""

import logging
from time import gmtime
from time import strftime

# Import Oauth2ClientBackend from oauth2_xfel_client
from oauth2_xfel_client.oauth2_client_backend import Oauth2ClientBackend

# Import common classes
from .common.config import EMAIL_HEADER, DEF_HEADERS
from .common.util import Util
# Import Calibration classes
from .modules.calibration import Calibration
from .modules.calibration_constant import CalibrationConstant
from .modules.calibration_constant_version import CalibrationConstantVersion
from .modules.condition import Condition
from .modules.device_type import DeviceType
from .modules.parameter import Parameter
from .modules.physical_device import PhysicalDevice


class CalibrationClient(Calibration,
                        CalibrationConstant,
                        CalibrationConstantVersion,
                        Condition, Parameter,
                        DeviceType, PhysicalDevice):
    def __init__(self,
                 client_id, client_secret,
                 token_url, refresh_url, auth_url, scope,
                 user_email, base_api_url,
                 session_token=None):
        self.oauth_client = Oauth2ClientBackend(client_id=client_id,
                                                client_secret=client_secret,
                                                scope=scope,
                                                token_url=token_url,
                                                refresh_url=refresh_url,
                                                auth_url=auth_url,
                                                session_token=session_token)

        self.headers = DEF_HEADERS
        self.headers.update({EMAIL_HEADER: user_email})
        self.headers.update(self.oauth_client.headers)

        self.base_api_url = base_api_url

    @staticmethod
    def set_calibration_constant(cal_client, condition, cc_h):
        logging.debug('condition: {0}'.format(condition))
        logging.debug('calibration_constant: {0}'.format(cc_h))

        #
        calibration_name = cc_h['calibration_name']
        resp = Calibration.get_by_name(cal_client, calibration_name)
        calibration_id = resp['data']['id']

        device_type_name = cc_h['device_type_name']
        resp = DeviceType.get_by_name(cal_client, device_type_name)
        device_type_id = resp['data']['id']

        condition_name = condition['name']
        condition_id = condition['id']

        # Generate unique name if it doesn't exist
        cc_name_01 = '{0}_{1}'.format(device_type_name, calibration_name)
        cc_name_uk = '{0}_{1}'.format(cc_name_01[:40], condition_name[:19])
        cc_name = Util.get_opt_hash_val(cc_h, 'name', cc_name_uk)

        #
        cc_desc = Util.get_opt_hash_val(cc_h, 'description')
        cc_flg_auto_approve = Util.val_to_api_bool(cc_h['flg_auto_approve'])
        cc_flg_avail = Util.get_opt_hash_val(cc_h, 'flg_available', 'true')

        cal_cc = {
            'name': cc_name,
            'calibration_id': str(calibration_id),
            'device_type_id': str(device_type_id),
            'condition_id': str(condition_id),
            'flg_auto_approve': cc_flg_auto_approve,
            'flg_available': cc_flg_avail,
            'description': cc_desc
        }
        logging.debug('Built Calibration CC: {0}'.format(cal_cc))

        #
        # SET cc from dictionary
        #
        return CalibrationConstant.set_from_dict(cal_client, cal_cc)

    @staticmethod
    def set_calibration_constant_version(cal_client,
                                         calibration_constant_id, ccv_h):
        logging.debug('calib_const_id: {0}'.format(calibration_constant_id))
        logging.debug('Calibration Constant Version Dict: {0}'.format(ccv_h))

        # Generate unique name if it doesn't exist
        datetime_str = strftime('%Y%m%d_%H%M%S', gmtime())
        cc_name_uk = '{0}_sIdx={1}'.format(datetime_str, ccv_h['start_idx'])
        cc_name = Util.get_opt_hash_val(ccv_h, 'name', cc_name_uk)

        #
        ccv_desc = Util.get_opt_hash_val(ccv_h, 'description')
        ccv_flg_good_quality = Util.val_to_api_bool(ccv_h['flg_good_quality'])
        ccv_flg_deployed = Util.get_opt_hash_val(ccv_h, 'flg_deployed',
                                                 def_val='true')

        physical_device_name = ccv_h['device_name']
        resp = PhysicalDevice.get_by_name(cal_client, physical_device_name)
        physical_device_id = resp['data']['id']

        cal_ccv = {
            'name': cc_name,
            'file_name': ccv_h['file_name'],
            'path_to_file': ccv_h['path_to_file'],
            'data_set_name': ccv_h['data_set_name'],
            'calibration_constant_id': str(calibration_constant_id),
            'physical_device_id': str(physical_device_id),
            'flg_deployed': ccv_flg_deployed,
            'flg_good_quality': ccv_flg_good_quality,
            'begin_validity_at': ccv_h['begin_validity_at'],
            'end_validity_at': ccv_h['end_validity_at'],
            'begin_at': ccv_h['begin_at'],
            'start_idx': ccv_h['start_idx'],
            'end_idx': ccv_h['end_idx'],
            'raw_data_location': ccv_h['raw_data_location'],
            'description': ccv_desc
        }
        logging.debug('Built Calibration CCV: {0}'.format(cal_ccv))

        #
        # Create new ccv from dictionary
        #
        return CalibrationConstantVersion.create_from_dict(cal_client, cal_ccv)

    @staticmethod
    def set_condition_from_dict(cal_client, detector_condition):
        cal_cond = CalibrationClient.get_condition_from_dict(
            cal_client,
            detector_condition
        )

        return Condition.set_condition_from_dict(cal_client, cal_cond)

    @staticmethod
    def search_condition_from_dict(cal_client, event_at, detector_condition):
        cal_cond = CalibrationClient.get_condition_from_dict(
            cal_client,
            detector_condition
        )

        cond = Condition(cal_client,
                         cal_cond['name'],
                         cal_cond['flg_available'],
                         event_at,
                         cal_cond['parameters_conditions_attributes'],
                         cal_cond['description'])

        resp = cond.get_expected()
        if resp['success']:
            return resp
        else:
            resp = cond.get_possible()

            if resp['success']:
                # This method returns several conditions over time
                # ordered by the closest condition creation datetime,
                # compared with the desired event datetime!
                # The closest condition is received in the first position!
                resp['data'] = resp['data'][0]

            return resp

    @staticmethod
    def search_possible_conditions_from_dict(cal_client,
                                             event_at,
                                             detector_condition):
        cal_cond = CalibrationClient.get_condition_from_dict(
            cal_client,
            detector_condition
        )

        cond = Condition(cal_client,
                         cal_cond['name'],
                         cal_cond['flg_available'],
                         event_at,
                         cal_cond['parameters_conditions_attributes'],
                         cal_cond['description'])

        resp = cond.get_possible()
        # This method returns several conditions over time
        # ordered by the closest condition creation datetime,
        # compared with the desired event datetime!

        return resp

    @staticmethod
    def get_condition_from_dict(cal_client, detector_condition):
        parameters_conditions = []

        for param in detector_condition['parameters']:
            param_name = param['parameter_name']
            param_desc = Util.get_opt_hash_val(param, 'description')

            resp = Parameter.get_by_name(cal_client, param_name)
            param_id = resp['data']['id']

            parameter_condition = {
                'parameter_id': str(param_id),
                'value': str(param['value']),
                'lower_deviation_value': str(param['lower_deviation_value']),
                'upper_deviation_value': str(param['upper_deviation_value']),
                'flg_available': Util.val_to_api_bool(param['flg_available']),
                'description': str(param_desc)
            }

            logging.debug('Build parameter_condition hash successfully')
            parameters_conditions.append(parameter_condition)

        curr_dt = Util.get_formatted_date('%Y-%m-%d %H:%M:%S')
        def_cond_name = '{0}'.format(curr_dt)
        condition_name = Util.get_opt_hash_val(detector_condition, 'name',
                                               def_val=def_cond_name)

        condition_flg_avail = Util.get_opt_hash_val(detector_condition,
                                                    'flg_available',
                                                    def_val='true')
        condition_desc = Util.get_opt_hash_val(detector_condition,
                                               'description')

        #
        cal_cond = {
            'name': condition_name,
            'flg_available': condition_flg_avail,
            'description': condition_desc,
            'parameters_conditions_attributes': parameters_conditions
        }
        logging.debug('Build condition successfully: {0}'.format(cal_cond))

        return cal_cond

    @staticmethod
    def inject_new_calibration_constant_version(cal_client, inject_h):
        logging.debug('Calibration injection hash is: {0}'.format(inject_h))

        # Separate the inject_h into its main elements
        inj_detector_condition = inject_h['detector_condition']
        inj_cal_const = inject_h['calibration_constant']
        inj_cal_const_version = inject_h['calibration_constant_version']

        # set_condition
        resp = CalibrationClient.set_condition_from_dict(
            cal_client,
            inj_detector_condition
        )

        if resp['success']:
            condition = resp['data']
            condition_id = condition['id']

            success_msg = 'condition_id: {0}'.format(condition_id)
            logging.debug(success_msg)
        else:
            error_msg = '{0} >> {1}'.format(resp['info'], resp['app_info'])
            logging.error(error_msg)
            return resp

        # set_calibration_constant
        resp = CalibrationClient.set_calibration_constant(cal_client,
                                                          condition,
                                                          inj_cal_const)
        if resp['success']:
            cal_calibration_constant = resp['data']
            cc_id = cal_calibration_constant['id']

            success_msg = 'condition_id: {0}'.format(cc_id)
            logging.debug(success_msg)
        else:
            error_msg = '{0} >> {1}'.format(resp['info'], resp['app_info'])
            logging.error(error_msg)
            return resp

        # create_calibration_constant_version
        resp = CalibrationClient.set_calibration_constant_version(
            cal_client,
            cc_id,
            inj_cal_const_version
        )

        if resp['success']:
            cal_calibration_constant_version = resp['data']
            ccv_id = cal_calibration_constant_version['id']

            success_msg = 'condition_id: {0}'.format(ccv_id)
            logging.debug(success_msg)
        else:
            error_msg = '{0} >> {1}'.format(resp['info'], resp['app_info'])
            logging.error(error_msg)
            return resp

        # In case of success
        return resp

    @staticmethod
    def retrieve_calibration_constant_version(cal_client, retrieve_h):
        logging.debug('Calibration retrieve hash is: {0}'.format(retrieve_h))

        # Separate the inject_h into its main elements
        ret_detector_condition = retrieve_h['detector_condition']

        # Calculate necessary values
        calibration_name = retrieve_h['calibration_name']
        device_name = retrieve_h['device_name']
        event_at = Util.get_opt_hash_val(retrieve_h, 'measured_at')
        snapshot_at = Util.get_opt_hash_val(retrieve_h, 'snapshot_at')

        # get_condition a valid condition
        resp = CalibrationClient.search_possible_conditions_from_dict(
            cal_client,
            event_at,
            ret_detector_condition)

        if resp['success']:
            conditions = resp['data']

            condition_ids = []
            for condition in conditions:
                condition_ids.append(condition['id'])

            success_msg = 'condition_ids: {0}'.format(condition_ids)
            logging.debug(success_msg)
        else:
            error_msg = '{0} >> {1}'.format(resp['info'], resp['app_info'])
            logging.error(error_msg)
            return resp

        # Get Calibration ID
        resp = Calibration.get_by_name(cal_client, calibration_name)
        if resp['success']:
            calibration = resp['data']
            calibration_id = calibration['id']

            success_msg = 'condition_id: {0}'.format(calibration_id)
            logging.debug(success_msg)
        else:
            error_msg = '{0} >> {1}'.format(resp['info'], resp['app_info'])
            logging.error(error_msg)
            return resp

        # Get PhysicalDevice ID and DeviceType ID
        resp = PhysicalDevice.get_by_name(cal_client, device_name)
        if resp['success']:
            device_id = resp['data']['id']
            device_type_id = resp['data']['device_type_id']

            success_msg = 'device_id: {0}'.format(device_id)
            logging.debug(success_msg)

            success_msg = 'device_type_id: {0}'.format(device_type_id)
            logging.debug(success_msg)
        else:
            error_msg = '{0} >> {1}'.format(resp['info'], resp['app_info'])
            logging.error(error_msg)
            return resp

        # Get CalibrationConstant ID
        resp = CalibrationConstant.get_all_by_conditions(cal_client,
                                                         calibration_id,
                                                         device_type_id,
                                                         condition_ids)
        if resp['success']:
            calibration_constants = resp['data']

            cc_ids = []
            for cc in calibration_constants:
                cc_ids.append(cc['id'])

            success_msg = 'calibration_constant_ids: {0}'.format(cc_ids)
            logging.debug(success_msg)
        else:
            error_msg = '{0} >> {1}'.format(resp['info'], resp['app_info'])
            logging.error(error_msg)
            return resp

        # Debug IDs
        logging.debug('* condition_ids == {0}'.format(condition_ids))
        logging.debug('* calibration_id == {0}'.format(calibration_id))
        logging.debug('* device_id == {0}'.format(device_id))
        logging.debug('* device_type_id == {0}'.format(device_type_id))
        logging.debug('* calibration_constant_ids == {0}'.format(cc_ids))

        # Get calibration_constant_version
        resp = CalibrationConstantVersion.get_closest_by_time(cal_client,
                                                              cc_ids,
                                                              device_id,
                                                              event_at,
                                                              snapshot_at)
        if resp['success']:
            calibration_constant_version = resp['data']
            ccv_id = calibration_constant_version['id']

            success_msg = 'calibration_constant_version_id: {0}'.format(ccv_id)
            logging.debug(success_msg)
        else:
            error_msg = '{0} >> {1}'.format(resp['info'], resp['app_info'])
            logging.error(error_msg)
            return resp

        # In case of success
        return resp

    @staticmethod
    def retrieve_all_calibration_constant_versions(cal_client, retrieve_h):
        logging.debug('Calibration retrieve hash is: {0}'.format(retrieve_h))

        # Separate the inject_h into its main elements
        ret_detector_condition = retrieve_h['detector_condition']

        # Calculate necessary values
        calibration_name = retrieve_h['calibration_name']
        device_name = retrieve_h['device_name']
        event_at = Util.get_opt_hash_val(retrieve_h, 'measured_at')
        snapshot_at = Util.get_opt_hash_val(retrieve_h, 'snapshot_at')

        # get_condition a valid condition
        resp = CalibrationClient.search_possible_conditions_from_dict(
            cal_client,
            event_at,
            ret_detector_condition
        )

        if resp['success']:
            conditions = resp['data']

            condition_ids = []
            for condition in conditions:
                condition_ids.append(condition['id'])

            success_msg = 'condition_ids: {0}'.format(condition_ids)
            logging.debug(success_msg)
        else:
            error_msg = '{0} >> {1}'.format(resp['info'], resp['app_info'])
            logging.error(error_msg)
            return resp

        # Get Calibration ID
        resp = Calibration.get_by_name(cal_client, calibration_name)
        if resp['success']:
            calibration = resp['data']
            calibration_id = calibration['id']

            success_msg = 'condition_id: {0}'.format(calibration_id)
            logging.debug(success_msg)
        else:
            error_msg = '{0} >> {1}'.format(resp['info'], resp['app_info'])
            logging.error(error_msg)
            return resp

        # Get PhysicalDevice ID and DeviceType ID
        resp = PhysicalDevice.get_by_name(cal_client, device_name)
        if resp['success']:
            device_id = resp['data']['id']
            device_type_id = resp['data']['device_type_id']

            success_msg = 'device_id: {0}'.format(device_id)
            logging.debug(success_msg)

            success_msg = 'device_type_id: {0}'.format(device_type_id)
            logging.debug(success_msg)
        else:
            error_msg = '{0} >> {1}'.format(resp['info'], resp['app_info'])
            logging.error(error_msg)
            return resp

        # Get CalibrationConstant ID
        resp = CalibrationConstant.get_all_by_conditions(cal_client,
                                                         calibration_id,
                                                         device_type_id,
                                                         condition_ids)
        if resp['success']:
            calibration_constants = resp['data']

            cc_ids = []
            for cc in calibration_constants:
                cc_ids.append(cc['id'])

            success_msg = 'calibration_constant_ids: {0}'.format(cc_ids)
            logging.debug(success_msg)
        else:
            error_msg = '{0} >> {1}'.format(resp['info'], resp['app_info'])
            logging.error(error_msg)
            return resp

        # Debug IDs
        logging.debug('* condition_ids == {0}'.format(condition_ids))
        logging.debug('* calibration_id == {0}'.format(calibration_id))
        logging.debug('* device_id == {0}'.format(device_id))
        logging.debug('* device_type_id == {0}'.format(device_type_id))
        logging.debug('* calibration_constant_ids == {0}'.format(cc_ids))

        # Get all calibration_constant_versions
        resp = CalibrationConstantVersion.get_all_versions(cal_client,
                                                           cc_ids,
                                                           device_id,
                                                           event_at,
                                                           snapshot_at)
        if resp['success']:
            success_msg = 'response successful!'
            logging.debug(success_msg)
        else:
            error_msg = '{0} >> {1}'.format(resp['info'], resp['app_info'])
            logging.error(error_msg)
            return resp

        # In case of success
        return resp

    @staticmethod
    def update_calibration_constant_version(cal_client, update_h):
        logging.debug('Calibration update hash is: {0}'.format(update_h))

        # Calculate necessary values
        ccv_id = update_h['ccv_id']

        # Get calibration_constant_version
        resp = CalibrationConstantVersion.get_by_id(cal_client, ccv_id)
        if resp['success']:
            ccv = resp['data']
            success_msg = 'retrieve_constant_version_id: {0}'.format(ccv_id)
            logging.debug(success_msg)
        else:
            error_msg = '{0} >> {1}'.format(resp['info'], resp['app_info'])
            logging.error(error_msg)
            return resp

        # Update calibration_constant_version
        # set parameters from DB
        ccv_pars = {k: v for k, v in ccv.items() if
                    (not isinstance(v, dict) and k != 'id')}
        ccv_pars['calibration_constant_id'] = ccv['calibration_constant']['id']
        ccv_pars['physical_device_id'] = ccv['physical_device']['id']

        # Update parameters
        updatable = ['description', 'end_idx', 'start_idx', 'begin_at',
                     'end_validity_at', 'begin_validity_at',
                     'flg_good_quality', 'flg_deployed']

        for key in updatable:
            if key in update_h:
                ccv_pars[key] = update_h[key]

        new_ccv = CalibrationConstantVersion(
            calibration_client=cal_client,
            **ccv_pars)

        new_ccv.id = ccv_id
        resp = new_ccv.update()

        if resp['success']:
            success_msg = 'update_constant_version_id: {0}'.format(ccv_id)
            logging.debug(success_msg)
        else:
            error_msg = '{0} >> {1}'.format(resp['info'], resp['app_info'])
            logging.error(error_msg)
            return resp

        # In case of success
        return resp
