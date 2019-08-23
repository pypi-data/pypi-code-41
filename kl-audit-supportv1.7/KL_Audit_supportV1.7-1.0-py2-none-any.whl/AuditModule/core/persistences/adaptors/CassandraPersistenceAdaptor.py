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
