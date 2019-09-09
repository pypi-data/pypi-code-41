from etlops.clients.mpp import SnowflakeClient
from pandas import DataFrame
import logging
import sys

'''
Because it is not possible to run a localhost instance of Snowflake, only private databases can be used to test the
classes.

Put the credentials of a Snowflake account as a dictionary in the SNOWFLAKE_CREDENTIALS_DICT constant or an absolute
path to it in the SF_CREDENTIALS_PATH in order to be able to run the tests.

Finally, fill all the fields of the CONTEXT dictionary. 
'''

format_str = "%(asctime)s  [%(levelname)-5.5s]  %(message)s"
logging.basicConfig(stream=sys.stderr, format=format_str, level=logging.INFO)
logging.getLogger('etlops').setLevel(logging.DEBUG)
logging.getLogger("snowflake.connector.network").disabled = True

SNOWFLAKE_CREDENTIALS_DICT = {"account":"",
                              "user":"",
                              "password":"",
                              "insecure_mode":False}
SNOWFLAKE_CREDENTIALS_PATH = None
CONTEXT={
        'database':'BF1',
        'role':'data_analyst',
        'schema':'public',
        'warehouse':'xs_query'
        }

DMLQueries = ['CREATE OR REPLACE TABLE test (a integer, b integer);',
              'INSERT INTO test values (1,2)',
              'INSERT INTO test values (1,3)']
SFClient = SnowflakeClient(SNOWFLAKE_CREDENTIALS_DICT)

if __name__ == '__main__':
    SFClient.connect()
    for Key, Value in CONTEXT.items():
        SFClient.switch_to(Key,Value)
    for DMLQuery in DMLQueries:
        SFClient.dml_query(DMLQuery)
    DF = SFClient.select_query('SELECT * from test;')
    assert(isinstance(DF , DataFrame))
    assert(len(DF == 2))

    SFClient.dml_query('DROP TABLE IF EXISTS test;')
    SFClient.disconnect()
