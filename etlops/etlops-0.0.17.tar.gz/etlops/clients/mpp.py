from etlops.clients.sql import SQLClient
from sqlalchemy import create_engine
from pandas import read_sql
import logging


class SnowflakeClient(SQLClient):
    SUSPENDED_WAREHOUSE_STATUS = ('SUSPENDED', 'SUSPENDING')
    USER_IDENTIFIER = 'user'
    PASSWORD_IDENTIFIER = 'password'
    ACCOUNT_IDENTIFIER = 'account'
    INSECURE_MODE = 'insecure_mode'
    WAREHOUSE = 'WAREHOUSE'
    SUSPEND_COMMAND = 'suspend'
    RESUME_COMMAND = 'resume'

    def __init__(self, config):
        if isinstance(config, str):
            self.configuration_dict = self._load_configuration_file(config)
        elif isinstance(config, dict):
            self.configuration_dict = config
        self.sql_alchemy_connection = None
        self.__set_sql_aqlchemy_engine()
        self.logger = logging.getLogger('SnowflakeClient')

    def __set_sql_aqlchemy_engine(self):
        self.sql_alchemy_engine = create_engine('snowflake://{user}:{password}@{account}/'.format(
            user=self.configuration_dict[self.USER_IDENTIFIER],
            password=self.configuration_dict[self.PASSWORD_IDENTIFIER],
            account=self.configuration_dict[self.ACCOUNT_IDENTIFIER],
            ),
            connect_args={'insecure_mode': self.configuration_dict[self.INSECURE_MODE]}
        )

    def connect(self):
        self.sql_alchemy_connection = self.sql_alchemy_engine.connect()
        self.logger.info('Snowflake Connection Open')

    def disconnect(self):
        self.sql_alchemy_connection.close()
        self.logger.info('Snowflake Connection Closed')

    def switch_to(self, db_object, db_object_name):
        if db_object.upper() == self.WAREHOUSE:
            self.alter_warehouse(warehouse=db_object_name, action='resume')
        switching_query = "USE {OBJECT} {OBJECT_NAME};".format(OBJECT=db_object, OBJECT_NAME=db_object_name)
        self.sql_alchemy_connection.execute(switching_query)
        self.logger.info("Switched to {OBJECT} = {OBJECT_NAME} successfully".format(OBJECT=db_object, OBJECT_NAME=db_object_name))

    def __check_warehouse_state(self, warehouse) -> str:
        warehouse = warehouse.upper()
        warehouse_state_dataframe = self.select_query("SHOW WAREHOUSES LIKE '{WAREHOUSE}';".format(WAREHOUSE=warehouse))
        warehouse_state = warehouse_state_dataframe.loc[warehouse_state_dataframe["name"] == warehouse, "state"].values[0]
        return warehouse_state

    def dml_query(self, query_string):
        self.sql_alchemy_connection.execute(query_string)

    def select_query(self, query_string):
        return read_sql(query_string,
                        con=self.sql_alchemy_connection)

    def alter_warehouse(self, warehouse, action):
        status = self.__check_warehouse_state(warehouse)
        if action == self.SUSPEND_COMMAND and status not in self.SUSPENDED_WAREHOUSE_STATUS:
            self.__alter_warehouse_query(warehouse, self.SUSPEND_COMMAND)
        elif action == self.RESUME_COMMAND and status in self.SUSPENDED_WAREHOUSE_STATUS:
            self.__alter_warehouse_query(warehouse, self.RESUME_COMMAND)

    def __alter_warehouse_query(self, warehouse, command):
        self.dml_query('Alter warehouse {WAREHOUSE} {COMMAND};'.format(WAREHOUSE=warehouse, COMMAND=command))
