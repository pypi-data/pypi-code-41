import traceback
from AuditModule.util import Logging as LOGG

Logger = LOGG.get_logger()


class UserManagementACStrategies(object):
    def __init__(self):
        pass

    @staticmethod
    def generate_audit_data(strategy_json, configuration_data, application_context, operation_type):
        try:
            data_reference_field = strategy_json.get("strategies", {}).get(
                application_context, {}).get(operation_type, {}).get("reference_field", "")
            if data_reference_field == "":
                data = configuration_data
            else:
                data = configuration_data.get(data_reference_field, {})
            return data
        except Exception as e:
            Logger.error(str(e))