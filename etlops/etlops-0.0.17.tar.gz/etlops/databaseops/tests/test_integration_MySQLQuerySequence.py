from nose2.tools import such
import os
import json

from etlops.databaseops.mysql import MySQLTransaction
from etlops.clients.rdbms import MySQLClient
from etlops.utils import SQLQuerySet
from etlops.databaseops.tests.test_assets import constants

CREDENTIALS = {"host": "",
               "port": "",
               "user": "",
               "password": "",
               "charset": ""}

with such.A("MySQL Transaction integration tests") as mt:

    @mt.has_setup
    def setup():
        client = MySQLClient(CREDENTIALS)
        with open(os.path.join(constants.DB_OPS_TESTS_OPS_PATH, 'mysql_transaction.json'), 'r') as metadata_file:
            metadata = json.load(metadata_file)
        query_set = SQLQuerySet(metadata)
        query_set.fetch_queries()
        query_set.build_query_set()
        queries = query_set.get_query_set()
        mt.instance = MySQLTransaction(queries, client, metadata)

    with mt.having('an execute method'):
        @mt.should('not crash when running a transaction')
        def test(case):
              mt.instance.execute()

    mt.createTests(globals())
