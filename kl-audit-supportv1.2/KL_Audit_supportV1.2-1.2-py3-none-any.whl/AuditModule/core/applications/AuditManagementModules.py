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

        if op_type == "login":
            user_name, client_id, user_role_name, module, operations, parameter_lable, status = \
                audit_logs_user_access_strategies(strategy_json, content_type, application_data)

        elif op_type == "DbUpdate":
            user_name, client_id, user_role_name, module, operations, parameter_lable, status = \
                audit_logs_db_access_strategies(strategy_json, content_type, application_data)

        return user_name, client_id, user_role_name, module, operations, parameter_lable, status
    except Exception as e:
        audit_message = ""
        action = ""
        user_id = ""
        json_string = {}
        label = ""
        Logger.error('Error in audit Log modules ', str(e))
        return audit_message, action, user_id, json_string, label



def audit_logs_user_management_strategies(strategy_json, content_type, user_data):
    try:
        operation_type = ""
        audit_message = ""
        action = ""
        user_id = ""
        label = ""
        json_string = {}
        application_context = user_data.get("application_context", "")
        operation_type_reference_field = strategy_json.get("strategies", {}).get(
            application_context, {}).get("fields", {}).get("type", {}).get("reference_field", "")
        operation_type_field_type = strategy_json.get("strategies", {}).get(application_context, {}).get(
            "fields", {}).get("type", {}).get("field_type", "")

        if operation_type_field_type == "direct":
            operation_type = user_data.get(operation_type_reference_field, "")

        if application_context == "UserManagementAC":
            user_management_ac_obj = AuditUserManagementStrategies.UserManagementACStrategies()
            if operation_type == "delete":
                audit_message, user_id, json_string, label = \
                    user_management_ac_obj.generate_delete_message(strategy_json, user_data, application_context,
                                                                   operation_type)
                action = "Deletion"
            elif operation_type == "edit":
                audit_message, user_id, json_string, label = \
                    user_management_ac_obj.generate_edit_message(strategy_json, user_data, application_context,
                                                                 operation_type)
                action = "Change"
            else:
                audit_message, user_id, json_string, label = \
                    user_management_ac_obj.generate_add_message(strategy_json, user_data, application_context,
                                                                operation_type)
                action = "Creation"
        return audit_message[:-2], action, user_id, json_string, label
    except Exception as e:
        print((traceback.format_exc()))
        Logger.error('Error in fetching user management strategies', str(e))
        raise Exception(str(e))

def audit_logs_user_access_strategies(strategy_json, content_type, user_data):
    try:
        user_name = ""
        client_id = ""
        user_role_name = ""
        operations = ""
        module = ""
        parameter_lable = {}
        status = ""

        response = user_data['response_json']['data']
        user_name = response['user_name']
        operations = user_data.get("service_context", "")
        client_id = response.get("client_id", "")
        user_role_name = response.get("user_role_name", "")
        parameter_lable = response.get("parameter_lable", "")
        module = response.get("module", "")
        status = user_data['response_json'].get("status", "")
        return user_name, client_id, user_role_name, module, operations , parameter_lable, status

    except Exception as e:
        print((traceback.format_exc()))
        Logger.error("Error in user Access ", str(e))
        raise Exception(str(e))

def audit_logs_db_access_strategies(strategy_json, content_type, user_data):
    try:
        user_name = ""
        client_id = ""
        user_role_name = ""
        operations = ""
        module = ""
        parameter_lable = {}
        status = ""
        role_name = ""

        if 'query_json' in user_data:
            response = user_data['query_json']
            user_name = response.get("username", "")
            operations = user_data.get("action", "")
            client_id = response.get("client_id", "")
            user_role_name = response.get("userrole", "")
            if type(user_role_name) is list:
                user_role_name = user_role_name[0]
            parameter_lable = json.dumps(user_data)
            module = response.get("module", "")
            status = user_data['query_json'].get("status", "success")
        else:
            response = user_data['query']
            user_name = response.get("user_id", "")
            operations = user_data.get("action", "")
            module = user_data.get("module", "")
            client_id = response.get("client_id", "")
            user_role_name = response.get("userrole", "")
            if type(user_role_name) is list:
                user_role_name = user_role_name[0]
            parameter_lable = json.dumps(user_data)
            status = user_data.get("status", "success")

        return user_name, client_id, user_role_name, module, operations, parameter_lable, status
    except Exception as e:
        print((traceback.format_exc()))
        Logger.error("Error in DB access ", str(e))



