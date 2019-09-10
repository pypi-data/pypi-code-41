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
    DBUPDATES = config['CASSANDRA']['DbUpdate']
    USERACCESS = config['CASSANDRA']['UserAccess']
    CLUSTER = config['CASSANDRA']['cluster']
    KEYSPACE_NAME = config['CASSANDRA']['keyspace_name']
    SCADA_CREATE_STATEMENT = "CREATE TABLE IF NOT EXISTS audit_logs.scadatriggers( id text, time TIMESTAMP, client_address text, client_id text, host_name text, module text, operations text, parameter_lable text, server_address text, status text, time_zone text, user_name text, PRIMARY KEY (id, time) ) WITH CLUSTERING ORDER BY (time DESC);"
    USERACCESS_CREATE_STATEMENT = "CREATE TABLE IF NOT EXISTS audit_logs.useraccess( id text, time TIMESTAMP, client_address text, client_id text, host_name text, module text, operations text, parameter_lable text, server_address text, status text, time_zone text, user_name text, PRIMARY KEY (id, time) ) WITH CLUSTERING ORDER BY (time DESC);"
    DBUPDATES_CREATE_STATEMENT = "CREATE TABLE IF NOT EXISTS audit_logs.dbupdates( id text, time TIMESTAMP, client_address text, client_id text, host_name text, module text, operations text, parameter_lable text, server_address text, status text, time_zone text, user_name text, PRIMARY KEY (id, time) ) WITH CLUSTERING ORDER BY (time DESC);"

    CREATE_STATEMENT = "CREATE TABLE IF NOT EXISTS audit_logs.{}( user_name text, time TIMESTAMP, id int, client_id text, module text, " \
                       "operations text, parameter_lable text, status text, client_ip text, server_ip text, time_zone text, " \
                       "PRIMARY KEY ((user_name,client_id,module, operations, parameter_lable, status, client_ip, server_ip, time_zone), time) )" \
                       "WITH CLUSTERING ORDER BY (time DESC);"
    KEYSPACE_STATEMENT = "CREATE KEYSPACE if not exists audit_logs WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 3};"
    TABLE_INSERT_STATEMENT = "insert into audit_logs.{0}(id, time, name) values (?,?,?);"
    SELECT_STATEMENT = "select id from audit_logs.{} WHERE name = '{}' LIMIT 1;"
    TABLE_CHECK_STATEMENT = "CREATE TABLE audit_logs.{0}(id int, time timestamp, primary key((time), id) " \
                            ")WITH CLUSTERING ORDER BY (id DESC);"
    # INSERT_STATEMENT = "INSERT INTO audit_sample (user_name, time, client_id, operations, parameter_lable, status, user_role_name) values (?,?,?,?,?,?,?)"
    INSERT_STATEMENT = "insert into audit_logs.{0}(user_name, time, id, client_id, module, operations, parameter_lable, status, client_address, server_address, host_name, time_zone) values(?,?,?,?,?,?,?,?,?,?,?,?)"
    INSERT_DBUPDATE_STATEMENT = "INSERT INTO audit_logs.audit_dbupdates (user_name, time, client_id, module, operations, parameter_lable, status, user_role_name) values (?,?,?,?,?,?,?,?)"


class AuditConfiguration:
    # Blueprint:
    service_blueprint = "audit_configuration"
    # API Endpoints:
    api_get_model = "/iLens/model/audit"


class RequestMethods:
    GET = "GET"
    POST = "POST"


class AuditMappingConstants:
    audit_logs_mapping_json = {"DbUpdate": config['AUDIT_MAPPING']['DbUpdate'],
                               "UserAccess": config['AUDIT_MAPPING']['UserAccess']}
