from etlops.clients.sql import SQLClient
from sqlalchemy import create_engine
from pandas import read_sql, DataFrame
import logging


class MySQLClient(SQLClient):
    SUSPENDED_WAREHOUSE_STATUS = ('SUSPENDED', 'SUSPENDING')
    USER_IDENTIFIER = 'user'
    PASSWORD_IDENTIFIER = 'password'
    HOST_IDENTIFIER = 'host'
    PORT_IDENTIFIER = 'port'
    DATABASE_IDENTIFIER = 'database'
    CHARSET_IDENTIFIER = 'charset'

    PANDAS_TO_SQL_DEFAULT_IF_EXISTS_PARAMETER = 'append'
    PANDAS_TO_SQL_DEFAULT_INDEX_PARAMETER = False
    PANDAS_TO_SQL_DEFAULT_DTYPE_PARAMETER = None

    def __init__(self, config):
        if isinstance(config, str):
            self.configuration_dict = self._load_configuration_file(config)
        elif isinstance(config, dict):
            self.configuration_dict = config
        self.sql_alchemy_connection = None
        self.__set_sql_aqlchemy_engine()
        self.logger = logging.getLogger('MySQLClient')

    def __set_sql_aqlchemy_engine(self) -> None:
        self.sql_alchemy_engine = create_engine('mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}?charset={charset}'.format(
            user=self.configuration_dict[MySQLClient.USER_IDENTIFIER],
            password=self.configuration_dict[MySQLClient.PASSWORD_IDENTIFIER],
            host=self.configuration_dict[MySQLClient.HOST_IDENTIFIER],
            port=self.configuration_dict[MySQLClient.PORT_IDENTIFIER],
            database=self.configuration_dict[MySQLClient.DATABASE_IDENTIFIER],
            charset=self.configuration_dict[MySQLClient.CHARSET_IDENTIFIER]
            )
        )

    def connect(self) -> None:
        self.sql_alchemy_connection = self.sql_alchemy_engine.connect()
        self.logger.info('MySQL Connection Open')

    def disconnect(self) -> None:
        self.sql_alchemy_connection.close()
        self.logger.info('MySQL Connection Closed')

    def switch_to(self, db_object_name) -> None:
        switching_query = "USE {OBJECT_NAME};".format(OBJECT_NAME=db_object_name)
        self.sql_alchemy_connection.execute(switching_query)
        self.logger.info("Switched to {OBJECT_NAME} successfully".format(OBJECT_NAME=db_object_name))

    def dml_query(self, query_string) -> None:
        self.sql_alchemy_connection.execute(query_string)

    def select_query(self, query_string) -> DataFrame:
        return read_sql(query_string, con=self.sql_alchemy_connection)

    def pandas_bulk_insert(self,
                           dataset: DataFrame,
                           name: str,
                           if_exists: str = 'append',
                           index: bool = False,
                           dtype: dict = None,
                           method = "multi",
                           chunksize: int = 500) -> None:
        dataset.to_sql(name=name, con=self.sql_alchemy_connection, if_exists=if_exists, index=index, dtype=dtype, method=method,chunksize=chunksize)
