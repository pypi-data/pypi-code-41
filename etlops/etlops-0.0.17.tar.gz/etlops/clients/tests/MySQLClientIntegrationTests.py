from etlops.clients.RDBMS import MySQLClient
from pandas import DataFrame

'''
Put the credentials as a dictionary in the CREDENTIALS_DICT constant or an absolute
path to it in CREDENTIALS_PATH in order to be able to run the tests.

Finally, fill all the fields of the CONTEXT dictionary. 
'''

CREDENTIALS_DICT = {"host":"",
                    "port":"",
                    "user":"",
                    "password":""}
CREDENTIALS_PATH = None
CONTEXT={
        'database':'revenue'
        }

DMLQueries = ['CREATE TABLE test (a integer, b integer);',
              'INSERT INTO test values (1,2)',
              'INSERT INTO test values (1,3)']
client = MySQLClient(CREDENTIALS_DICT)

if __name__ == '__main__':
    client.connect()
    for Key, Value in CONTEXT.items():
        client.switch_to(Value)
    for DMLQuery in DMLQueries:
        client.dml_query(DMLQuery)
    DF = client.select_query('SELECT * from test;')
    assert(isinstance(DF , DataFrame))
    assert(len(DF == 2))

    client.dml_query('DROP TABLE IF EXISTS test;')
    client.disconnect()
