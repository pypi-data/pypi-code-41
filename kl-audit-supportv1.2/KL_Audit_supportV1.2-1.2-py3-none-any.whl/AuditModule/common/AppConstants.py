from datetime import datetime
from AuditModule.common.configuration_settings import config


class AuditLogsConstants:
    def __init__(self):
        pass

    audit_time_date_format = "%Y-%m-%d %H:%M:%S.%f"
    epoch_date = datetime(1970, 1, 1)
    application_type_json = {"login_handler": {"application_type": "login",
                                                  "type": "User Management"}}
    audit_logs_mapping_json = {
        "login_handler": {
            "strategies": {

            }

        },
        "user_managements": {
            "strategies": {
                "UserManagementAC": {
                    "fields": {
                        "type": {
                            "reference_field": "type_",
                            "field_name": "type",
                            "field_type": "direct"
                        },
                        "user_id": {
                            "reference_field": "submittedBy",
                            "field_name": "user_id",
                            "field_type": "direct"
                        }
                    },
                    "add": {
                        "reference_field": "input_json",
                        "label_field": "userId",
                        "message": "Created new user with fields ",
                        "type": "add",
                        "fields": {
                            "email_id": {
                                "reference_field": "emailId",
                                "field_name": "email_id",
                                "field_type": "direct",
                                "display_name": "Email ID"
                            },
                            "first_name": {
                                "reference_field": "firstName",
                                "field_name": "first_name",
                                "field_type": "direct",
                                "display_name": "First Name"
                            },
                            "last_name": {
                                "reference_field": "lastName",
                                "field_name": "last_name",
                                "field_type": "direct",
                                "display_name": "Last Name"
                            },
                            "user_id": {
                                "reference_field": "userId",
                                "field_name": "user_id",
                                "field_type": "direct",
                                "display_name": "User ID"
                            },
                            "role": {
                                "reference_field": "role",
                                "field_name": "itemName",
                                "field_type": "list_of_objects",
                                "display_name": "Role"
                            }
                        }
                    },
                    "edit": {
                        "reference_field": "input_json",
                        "label_field": "userId",
                        "message": "Updated User Details for User {user_id}. Changed ",
                        "type": "edit",
                        "fields": {
                            "email_id": {
                                "reference_field": "emailId",
                                "field_name": "email_id",
                                "field_type": "direct",
                                "display_name": "Email ID",
                                "database_reference_field": "email_id"
                            },
                            "first_name": {
                                "reference_field": "firstName",
                                "field_name": "first_name",
                                "field_type": "direct",
                                "display_name": "First Name",
                                "database_reference_field": "first_name"
                            },
                            "last_name": {
                                "reference_field": "lastName",
                                "field_name": "last_name",
                                "field_type": "direct",
                                "display_name": "Last Name",
                                "database_reference_field": "last_name"
                            },
                            "user_id": {
                                "reference_field": "userId",
                                "field_name": "user_id",
                                "field_type": "direct",
                                "display_name": "User ID",
                                "database_reference_field": "user_id"
                            },
                            "mobile_number": {
                                "reference_field": "mobNumber",
                                "field_name": "mobile_number",
                                "field_type": "direct",
                                "display_name": "Mobile Number",
                                "database_reference_field": "mob_number"
                            },
                            "role": {
                                "reference_field": "role",
                                "field_name": "itemName",
                                "field_type": "list_of_objects",
                                "display_name": "Role",
                                "database_reference_field": "role"
                            },
                            "password": {
                                "reference_field": "password",
                                "field_name": "password",
                                "field_type": "direct",
                                "display_name": "Password",
                                "database_reference_field": "password"
                            }
                        }
                    },
                    "delete": {
                        "label_field": "user_id",
                        "reference_field": "input_json",
                        "message": "Deleted user with ",
                        "type": "delete",
                        "fields": {
                            "user_id": {
                                "reference_field": "user_id",
                                "field_name": "user_id",
                                "field_type": "direct",
                                "display_name": "User ID"
                            }
                        }
                    }
                }
            }
        }}

class CassandraConstants:
    CLUSTER = config['CASSANDRA']['cluster']
    KEYSPACE_NAME = config['CASSANDRA']['keyspace_name']
    # INSERT_STATEMENT = "INSERT INTO audit_sample (user_name, time, client_id, operations, parameter_lable, status, user_role_name) values (?,?,?,?,?,?,?)"
    INSERT_USERACCESS_STATEMENT = "INSERT INTO audit_useraccess (user_name, timedate, client_id, module, operations, parameter_lable, status, user_role_name) values (?,?,?,?,?,?,?,?)"
    INSERT_DBUPDATE_STATEMENT = "INSERT INTO audit_dbupdates (user_name, timedate, client_id, module, operations, parameter_lable, status, user_role_name) values (?,?,?,?,?,?,?,?)"
class AuditConfiguration:
    # Blueprint:
    service_blueprint = "audit_configuration"
    # API Endpoints:
    api_get_model = "/iLens/model/audit"

class RequestMethods:
    GET = "GET"
    POST = "POST"