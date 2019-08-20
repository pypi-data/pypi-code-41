import inspect
from AuditModule.core.applications import Annotations
from AuditModule.util import Logging as LOGG
from AuditModule.common import AppConstants
# from bin.util import CommonUtils
from AuditModule.core.applications import AuditManagementModules
from AuditModule.core.persistences import PersistenceAdaptor
import traceback
import json
from datetime import datetime
from _thread import *
from AuditModule.common.configuration_settings import config

__all__ = {"start_new_thread"}
Logger = LOGG.get_logger()
op_type = config['OPERATION']['op_type']
audit_management_obj = PersistenceAdaptor.get_instance('CassandraDButility')


class Audit():
    def save_audit_entry(self,op_type):
        """
        This method is for saving audit entry in the database
        """
        try:
            Logger.debug('Initializing the auditing')
            function_call_stack_frame_data = Annotations.fetch_function_stack_frame(inspect.stack())
            application_type = self.fetch_application_type(function_call_stack_frame_data)
            content_type = self.fetch_content_type(function_call_stack_frame_data)
            start_new_thread(self.save_audit_entry_impl, (application_type, content_type, function_call_stack_frame_data, op_type))
        except Exception as e:
            print((traceback.format_exc()))
            Logger.error('Error in auditing', str(e))

    @staticmethod
    def fetch_application_type(function_call_stack_frame_data):
        """
        This method fetches the application type based on the application context
        :param function_call_stack_frame_data: Function call stack frame data
        :return: Application type
        """
        try:
            application_context = function_call_stack_frame_data.get("application_context", "")
            application_type = AppConstants.AuditLogsConstants.application_type_json.get(
                application_context, {}).get("application_type", "")
            print("application_context", application_context)
            print("------", application_type)
            Logger.debug('Application type is {}'.format(application_type))
            return application_type
        except Exception as e:
            print((traceback.format_exc()))
            Logger.error('Error in fetching application type ',str(e))

    @staticmethod
    def fetch_content_type(function_call_stack_frame_data):
        """
        This method fetches the application type based on the application context
        :param function_call_stack_frame_data: Function call stack frame data
        :return: Application type
        """
        try:
            application_context = function_call_stack_frame_data.get("application_context", "")
            application_type = AppConstants.AuditLogsConstants.application_type_json.get(
                application_context, {}).get("type", "")
            Logger.debug('Content type is {}'.format(application_type))
            return application_type
        except Exception as e:
            print((traceback.format_exc()))
            Logger.error('Error in fetching content type ', str(e))

    @staticmethod
    def save_audit_entry_impl(application_type, content_type, function_call_stack_frame_data, op_type):
        try:
            data = dict()

            user_name, client_id, user_role_name, module,operations, parameter_lable, status = \
                AuditManagementModules.audit_logs_modules(application_type, content_type,
                                                                  function_call_stack_frame_data, op_type)

            data["user_name"] = user_name
            data['client_id'] = client_id
            data['user_role_name'] = user_role_name
            data['module'] = module
            data['operations'] = operations
            data['parameter_lable'] = json.dumps(parameter_lable)
            data['status'] = status
            data['module'] = op_type
            data['timedate'] = str(datetime.utcnow())
            if (user_name and user_name is not None):
                audit_management_obj.insert_record(data)
                Logger.debug('Auditing completed')
        except Exception as ex:
            Logger.error(str(ex))
