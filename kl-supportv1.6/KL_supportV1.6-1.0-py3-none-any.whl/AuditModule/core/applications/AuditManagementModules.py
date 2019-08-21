from AuditModule.common import AppConstants
from AuditModule.util import Logging as LOGG
import traceback
import json
from AuditModule.core.applications import AuditUserManagementStrategies

Logger = LOGG.get_logger()


def audit_logs_modules(application_type, content_type, application_data, op_type):
    try:
        user_name = ""
        client_id = ""
        user_role_name = ""
        operations = ""
        module = ""
        parameter_lable = {}
        status = ""
        strategy_json = AppConstants.AuditLogsConstants.audit_logs_mapping_json.get(application_type)

        user_name, client_id, user_role_name, module, operations, parameter_lable, status = \
            audit_logs_user_access_strategies(strategy_json, content_type, application_data)

        return user_name, client_id, user_role_name, module, operations, parameter_lable, status
    except Exception as e:
        audit_message = ""
        action = ""
        user_id = ""
        json_string = {}
        label = ""
        Logger.error('Error in audit Log modules ', str(e))
        return audit_message, action, user_id, json_string, label


def audit_logs_user_access_strategies(strategy_json, content_type, user_data):
    try:
        user_name = ""
        client_id = ""
        user_role_name = ""
        operations = ""
        module = ""
        parameter_lable = {}
        status = ""

        if 'query_json' in user_data:
            response = user_data.get('query_json', "")
            if type(response) is not str:
                user_name = response.get('user_name', "")
            if not user_name and type(response) is not str:
                user_name = response.get('user_id', "")
            if not user_name and 'cookies' in user_data:
                user_name = user_data['cookies']['user_id']
            if not user_name and 'user_id' in user_data:
                user_name = user_data['user_id']
            operations = user_data.get("action", "")
            client_id = response.get("client_id", "")
            if not client_id and 'client_id' in user_data:
                client_id = user_data.get("client_id", "")
            user_role_name = response.get("user_role_name", "")
            parameter_lable = user_data
            module = response.get("module", "")
            status = user_data['query_json'].get("status", "success")
        return user_name, client_id, user_role_name, module, operations, parameter_lable, status

    except Exception as e:
        print((traceback.format_exc()))
        Logger.error("Error in user Access ", str(e))
        raise Exception(str(e))



