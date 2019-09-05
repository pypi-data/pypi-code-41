import traceback
import json

from cassandra.cluster import Cluster
from AuditModule.common import AppConstants
from AuditModule.util import Logging as LOGG

Logger = LOGG.get_logger()

class CassandraDButility:
    def __init__(self):
        """
            Initializer
        """
        try:
            Logger.info("Initializing DB connection")
            self.cluster = Cluster(AppConstants.CassandraConstants.CLUSTER)
            self.session = self.cluster.connect(AppConstants.CassandraConstants.KEYSPACE_NAME)
        except Exception as e:
            Logger.error("Exception in the cassandradb initialization" + str(e))
            traceback.print_exc()

    def table_check(self, table):
        try:
            Logger.info("entered in to table check function")
            insert_statement = """
                CREATE TABLE {0}(id int, time timestamp,name text,
                PRIMARY KEY(name, id))
                WITH CLUSTERING ORDER BY (id DESC)""".format(table)
            self.session.execute(insert_statement)
            Logger.info("Table check completed")
            return True
        except Exception as e:
            Logger.exception("Exception occured while cheking or creating the table" + str(e))
            return False

    def insert_table_id(self, table, json_obj):
        try:
            insert_statment = self.session.prepare(AppConstants.CassandraConstants.TABLE_INSERT_STATEMENT.format(table))
            self.session.execute(insert_statment, json_obj)
            Logger.info("Data inserted successfully")
            return True
        except Exception as e:
            Logger.exception("Exception while inserting the data " + str(e))
            return False

    def fetch_table_id(self, table):
        try:
            insert_statement = self.session.prepare(
                AppConstants.CassandraConstants.SELECT_STATEMENT.format(table, table))
            response = self.session.execute(insert_statement)
            return response.current_rows
        except Exception as e:
            traceback.print_exc()
            raise Exception(str(e))

    def insert_record(self, json_obj, table):
        """
            sample json
            {
            "id": "",
            "lable": "",
        :param json:
        :return:
        """
        try:
            insert_statment = self.session.prepare(AppConstants.CassandraConstants.INSERT_STATEMENT.format(table))
            self.session.execute(insert_statment, json_obj)
            Logger.info("Data inserted successfully")
            return True
        except Exception as e:
            Logger.exception("Exception while inserting the data " + str(e))
            return False
