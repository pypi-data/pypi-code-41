import datetime
import urllib

import pyodbc
import pandas as pd

from sqlalchemy import create_engine

# DB connection parameters
username = ''
password = ''

'''
First (write) function require to specify:
data to write- pd.DataFrame (pd.DataFrame column names must match DB table column names)
connection parameters - username, password and database
query parameters - table to update name
'''

def write_df_to_sql(df, username=username, password=password, database='', table=''):
    # Add datestamp to df
    df.insert(0, 'update_date', datetime.date.today()) 

    # Setup connection parameters
    
    db = database
    u = username
    p = password
    driver= '{ODBC Driver 17 for SQL Server}'

    connection_string = 'DRIVER=' + driver + \
                        ';SERVER=' + s + \
                        ';PORT=1433' + \
                        ';DATABASE=' + db + \
                        ';UID=' + u + \
                        ';PWD=' + p 

    params = urllib.parse.quote_plus(connection_string)

    engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params, fast_executemany=True)

    # Write (update) df to database.table
    df.to_sql(table, con = engine, if_exists = 'append', index = False, chunksize=10000)

'''
Second (read) function require to specify:
query to DB - standard SQL query as string (ex. 'SELECT * FROM my_table')
connection parameters - username, password and database

return - pandas DataFrame
'''

def read_sql_to_df (query='', username=username, password=password, database='',server=""):
    # Setup connection parameters

    db = database
    u = username
    p = password
    s = server
    driver= '{ODBC Driver 17 for SQL Server}'

    connection_string = 'DRIVER=' + driver + \
                    ';SERVER=' + s + \
                    ';PORT=1433' + \
                    ';DATABASE=' + db + \
                    ';UID=' + u + \
                    ';PWD=' + p 
    params = urllib.parse.quote_plus(connection_string)
    engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params, fast_executemany=True)

    # Read from database
    temp_df = pd.read_sql(query, engine)

    return temp_df

'''
Third (query) function require to specify:
query to DB - standard SQL query as string (ex. 'SELECT * FROM my_table')
connection parameters - username, password and database

Useful for delete, alter update and insert options
'''
def query_sql_without_return(query='', username=username, password=password, database=''):
    # Setup connection parameters
    
    db = database
    u = username
    p = password
    driver= '{ODBC Driver 17 for SQL Server}'

    connection_string = 'DRIVER=' + driver + \
                    ';SERVER=' + s + \
                    ';PORT=1433' + \
                    ';DATABASE=' + db + \
                    ';UID=' + u + \
                    ';PWD=' + p 
    params = urllib.parse.quote_plus(connection_string)
    engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params, fast_executemany=True)

    # Execute query
    connection = engine.connect()
    connection.execute(query)
    connection.close()
# ----------------------------- Testing --------------------------------------------------------------------------------------

# # Write example
# item_ean = pd.read_csv('EAN_CODES.csv', encoding='ISO-8859-2')
# write_df_to_sql(item_ean, database=database, table=table)

# # Read example
# query = 'select * from carrefour_ean_input'
# my_df = read_sql_to_df(query, database=database)

# # Insert example
# query = 'insert into my_test (update_date, second) values (\'20201006\', 5)'
# query_sql_without_return(query, database='ds_team_ognjen')

# # Delete example
# query = 'delete from my_test'
# query_sql_without_return(query, database='ds_team_ognjen')
