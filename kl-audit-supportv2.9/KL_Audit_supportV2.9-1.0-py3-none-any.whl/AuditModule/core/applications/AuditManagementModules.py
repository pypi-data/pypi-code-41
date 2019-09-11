from AuditModule.common import AppConstants
from AuditModule.util import Logging as LOGG
import traceback
from datetime import datetime
from AuditModule.core.persistences.adaptors.CassandraPersistenceAdaptor import CassandraDButility
cassandra_obj = CassandraDButility()

Logger = LOGG.get_logger()


def audit_logs_modules(application_type, content_type, application_data):
    try:
        user_name = ""
        client_id = ""
        user_role_name = ""
        operations = ""
        module = ""
        parameter_lable = {}
        status = ""
        strategy_json = AppConstants.AuditLogsConstants.audit_logs_mapping_json.get(application_type)

        user_name, client_id, user_role_name, operations, parameter_lable, status = \
            audit_logs_user_access_strategies(application_data)

        return user_name, client_id, user_role_name, operations, parameter_lable, status
    except Exception as e:
        audit_message = ""
        action = ""
        user_id = ""
        json_string = {}
        label = ""
        Logger.error('Error in audit Log modules ', str(e))
        return audit_message, action, user_id, json_string, label


def audit_logs_user_access_strategies(user_data):
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
                if type(user_data.get('user_id')) is dict:
                    user_name = user_data['user_id'].get("user_id", "")
            operations = user_data.get("action", "")
            client_id = response.get("client_id", "")
            if not client_id and 'client_id' in user_data:
                client_id = user_data.get("client_id", "")
                if type(user_data.get('client_id')) is dict:
                    client_id = user_data['client_id'].get("client_id", "")
            user_role_name = response.get("user_role_name", "")
            parameter_lable = user_data['query_json']
            # module = response.get("module", "")
            status = user_data['query_json'].get("status", "success")
        return user_name, client_id, user_role_name, operations, parameter_lable, status
    except Exception as e:
        print((traceback.format_exc()))
        Logger.error("Error in user Access ", str(e))
        raise Exception(str(e))

def generate_id(table_name, op_type):
    try:
        if table_name:
            data = dict()
            check = cassandra_obj.table_check(table_name)
            if check:
                counter = 0
                data['id'] = counter + 1
                data['time'] = datetime.utcnow()
                data['name'] = "audit_id"
                cassandra_obj.insert_table_id(table_name, data)
                Logger.info("created and inserted data successfully")
                return data['id']
            else:
                name = "audit_id"
                response = cassandra_obj.fetch_table_id(name)
                for i in response:
                    resp_id = i[0]
                    data['id'] = resp_id + 1
                    data['time'] = datetime.utcnow()
                    data['name'] = name
                    cassandra_obj.insert_table_id(table_name, data)
                    Logger.info("updated data successfully")
                    return data['id']
    except Exception as e:
        print((traceback.format_exc()))
        Logger.error("Error in user Access ", str(e))
        raise Exception(str(e))