# -*- coding: utf-8 -*-

#  Copyright 2019-  DNB
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import sys
from robot.api import logger
from robot.api.deco import keyword



class Query(object):
    """
    Query handles all the querying done by the Database Library.
    """

    
    @keyword(name=None, tags=("Query",))
    def query(self, selectStatement, sansTran=False, returnAsDict=False):
        """
        *Uses the input `selectStatement` to query for the values that will be returned as a list of tuples.*
        
        Tip: Unless you want to log all column values of the specified rows, try specifying the column names in your select statements as much as possible to prevent any unnecessary surprises with schema
        changes and to easily see what your [] indexing is trying to retrieve
        (i.e. instead of `"select * from my_table"`, try `"select id, col_1, col_2 from my_table"`).
        
        *Arguments*

        ``selectStatement``: SELECT query 

        ``sansTran``: Optional. Set `sansTran` to True to run command without an explicit transaction commit or rollback.
        
        ``returnAsDict``: Optional. Set `returnAsDict` to True to return values as a list of dictionaries.
        
        *Examples*

        For example, given we have a table `person` with the following data:
        | id | first_name  | last_name |
        |  1 | Franz Allan | See       |

        When you do the following:
        | @{queryResults} | `Query` | SELECT * FROM person |
        | Log Many | @{queryResults} |

        You will get the following:
        [1, 'Franz Allan', 'See']

        Also, you can do something like this:
        | ${queryResults} | `Query` | SELECT first_name, last_name FROM person |
        | Log | ${queryResults[0][1]}, ${queryResults[0][0]} |

        And get the following
        See, Franz Allan

        Using optional `sansTran` to run command without an explicit transaction commit or rollback:
        | @{queryResults} | `Query` | SELECT * FROM person | True |
        """
        cur = None
        try:
            cur = self._dbconnection.cursor()
            logger.info('Executing : Query  |  %s ' % selectStatement)
            self.__execute_sql(cur, selectStatement)
            allRows = cur.fetchall()

            if returnAsDict:
                mappedRows = []
                col_names = [c[0] for c in cur.description]

                for rowIdx in range(len(allRows)):
                    d = {}
                    for colIdx in range(len(allRows[rowIdx])):
                        d[col_names[colIdx]] = allRows[rowIdx][colIdx]
                    mappedRows.append(d)
                return mappedRows

            return allRows
        finally:
            if cur:
                if not sansTran:
                    self._dbconnection.rollback()

    
    
    @keyword(name=None, tags=("Query",))
    def row_count(self, selectStatement, sansTran=False):
        """
        *Uses the input `selectStatement` to query the database and returns the number of rows from the query.*
        
        *Arguments*

        ``selectStatement``: SELECT query 

        ``sansTran``: Optional. Set `sansTran` to True to run command without an explicit transaction commit or rollback.

        *Examples*
        
        For example, given we have a table `person` with the following data:
        | id | first_name  | last_name |
        |  1 | Franz Allan | See       |
        |  2 | Jerry       | Schneider |

        When you do the following:
        | ${rowCount} | `Row Count` | SELECT * FROM person |
        | Log | ${rowCount} |

        You will get the following:
        2

        Also, you can do something like this:
        | ${rowCount} | `Row Count` | SELECT * FROM person WHERE id = 2 |
        | Log | ${rowCount} |

        And get the following
        1

        Using optional `sansTran` to run command without an explicit transaction commit or rollback:
        | ${rowCount} | `Row Count` | SELECT * FROM person | True |
        """
        cur = None
        try:
            cur = self._dbconnection.cursor()
            logger.info('Executing : Row Count  |  %s ' % selectStatement)
            self.__execute_sql(cur, selectStatement)
            data = cur.fetchall()
            if self.db_api_module_name in ["sqlite3", "ibm_db", "ibm_db_dbi", "pyodbc"]:
                rowCount = len(data)
            else:
                rowCount = cur.rowcount
            return rowCount
        finally:
            if cur:
                if not sansTran:
                    self._dbconnection.rollback()

    
    @keyword(name=None, tags=("Query",))
    def description(self, selectStatement, sansTran=False):
        """
        *Uses the input `selectStatement` to query a table in the db which will be used to determine the description.*
        
        *Arguments*

        ``selectStatement``: SELECT query 

        ``sansTran``: Optional. Set `sansTran` to True to run command without an explicit transaction commit or rollback.

        *Examples*

        For example, given we have a table `person` with the following data:
        | id | first_name  | last_name |
        |  1 | Franz Allan | See       |

        When you do the following:
        | @{queryResults} | `Description` | SELECT * FROM person |
        | Log Many | @{queryResults} |

        You will get the following:
        [Column(name='id', type_code=1043, display_size=None, internal_size=255, precision=None, scale=None, null_ok=None)]
        [Column(name='first_name', type_code=1043, display_size=None, internal_size=255, precision=None, scale=None, null_ok=None)]
        [Column(name='last_name', type_code=1043, display_size=None, internal_size=255, precision=None, scale=None, null_ok=None)]

        Using optional `sansTran` to run command without an explicit transaction commit or rollback:
        | @{queryResults} | `Description` | SELECT * FROM person | True |
        """
        cur = None
        try:
            cur = self._dbconnection.cursor()
            logger.info('Executing : Description  |  %s ' % selectStatement)
            self.__execute_sql(cur, selectStatement)
            description = list(cur.description)
            if sys.version_info[0] < 3:
                for row in range(0, len(description)):
                    description[row] = (description[row][0].encode('utf-8'),) + description[row][1:]
            return description
        finally:
            if cur:
                if not sansTran:
                    self._dbconnection.rollback()

    
    @keyword(name=None, tags=("Query",))
    def delete_all_rows_from_table(self, tableName, sansTran=False):
        """
        *Delete all the rows within a given table.*
        
        *Arguments*

        ``tableName``: Name of the table

        ``sansTran``: Optional. Set `sansTran` to True to run command without an explicit transaction commit or rollback.
        
        *Examples*
        
        For example, given we have a table `person` in a database

        When you do the following:
        | `Delete All Rows From Table` | person |

        If all the rows can be successfully deleted, then you will get:
        | `Delete All Rows From Table` | person | # PASS |
        
        If the table doesn't exist or all the data can't be deleted, then you will get:
        | `Delete All Rows From Table` | first_name | # FAIL |

        Using optional `sansTran` to run command without an explicit transaction commit or rollback:
        | `Delete All Rows From Table` | person | True |
        """
        cur = None
        selectStatement = ("DELETE FROM %s;" % tableName)
        try:
            cur = self._dbconnection.cursor()
            logger.info('Executing : Delete All Rows From Table  |  %s ' % selectStatement)
            result = self.__execute_sql(cur, selectStatement)
            if result is not None:
                if not sansTran:
                    self._dbconnection.commit()
                return result
            if not sansTran:
                self._dbconnection.commit()
        finally:
            if cur:
                if not sansTran:
                    self._dbconnection.rollback()

    
    @keyword(name=None, tags=("Query",))
    def execute_sql_script(self, sqlScriptFileName, sansTran=False):
        """
        *Executes the content of the `sqlScriptFileName` as SQL commands and returns number of rows affected. Useful for setting the database to a known state before running your tests, or clearing out your test
        data after running each a test.* 
        
        *Arguments*

        ``sqlScriptFileName``: Name and location of the script file to be executed.

        ``sansTran``: Optional. Set `sansTran` to True to run command without an explicit transaction commit or rollback.
        
        *Examples*

        | `Execute Sql Script` | ${EXECDIR}${/}resources${/}DDL-setup.sql |
        | `Execute Sql Script` | ${EXECDIR}${/}resources${/}DML-setup.sql |
        | `Execute Sql Script` | ${EXECDIR}${/}resources${/}DML-teardown.sql |
        | `Execute Sql Script` | ${EXECDIR}${/}resources${/}DDL-teardown.sql |

        SQL commands are expected to be delimited by a semi-colon (';').

        For example:
        DELETE FROM person_employee_table;
        DELETE FROM person_table;
        DELETE FROM employee_table;

        Also, the last SQL command can optionally omit its trailing semi-colon.

        For example:
        DELETE FROM person_employee_table;
        DELETE FROM person_table;
        DELETE FROM employee_table

        Given this, that means you can create spread your SQL commands in several lines.

        For example:
        DELETE
          FROM person_employee_table;
        DELETE
          FROM person_table;
        DELETE
          FROM employee_table

        However, lines that starts with a number sign (`#`) are treated as a
        commented line. Thus, none of the contents of that line will be executed.

        For example:
        # Delete the bridging table first...
        DELETE
          FROM person_employee_table;
          # ...and then the bridged tables.
        DELETE
          FROM person_table;
        DELETE
          FROM employee_table

        Using optional `sansTran` to run command without an explicit transaction commit or rollback:
        | `Execute Sql Script` | ${EXECDIR}${/}resources${/}DDL-setup.sql | True |
        """
        sqlScriptFile = open(sqlScriptFileName)

        cur = None
        result = 0
        try:
            cur = self._dbconnection.cursor()
            logger.info('Executing : Execute SQL Script  |  %s ' % sqlScriptFileName)
            sqlStatement = ''
            for line in sqlScriptFile:
                PY3K = sys.version_info >= (3, 0)
                if not PY3K:
                    #spName = spName.encode('ascii', 'ignore')
                    line = line.strip().decode("utf-8")
                if line.startswith('#'):
                    continue
                elif line.startswith('--'):
                    continue

                sqlFragments = line.split(';')
                if len(sqlFragments) == 1:
                    sqlStatement += line + ' '
                else:
                    for sqlFragment in sqlFragments:
                        sqlFragment = sqlFragment.strip()
                        if len(sqlFragment) == 0:
                            continue

                        sqlStatement += sqlFragment + ' '

                        result = result + self.__execute_sql(cur, sqlStatement)
                        sqlStatement = ''

            sqlStatement = sqlStatement.strip()
            if len(sqlStatement) != 0:
                result = self.__execute_sql(cur, sqlStatement)

            if not sansTran:
                self._dbconnection.commit()
        finally:
            if cur:
                if not sansTran:
                    self._dbconnection.rollback()
        return result

    
    @keyword(name=None, tags=("Query",))
    def execute_sql_string(self, sqlString, sansTran=False):
        """
        *Executes the sqlString as SQL commands  and returns number of rows affected. Useful to pass arguments to your sql.* 
        
        *Arguments*

        ``sqlString``: SQL statement to be executed.

        ``sansTran``: Optional. Set `sansTran` to True to run command without an explicit transaction commit or rollback.
        
        *Examples*        

        SQL commands are expected to be delimited by a semi-colon (';').

        For example:
        | `Execute Sql String` | DELETE FROM person_employee_table; DELETE FROM person_table |

        For example with an argument:
        | `Execute Sql String` | SELECT * FROM person WHERE first_name = ${FIRSTNAME} |

        Using optional `sansTran` to run command without an explicit transaction commit or rollback:
        | `Execute Sql String` | DELETE FROM person_employee_table; DELETE FROM person_table | True |
        """
        cur = None
        result = 0
        try:
            cur = self._dbconnection.cursor()
            logger.info('Executing : Execute SQL String  |  %s ' % sqlString)
            result = self.__execute_sql(cur, sqlString)
            if not sansTran:
                self._dbconnection.commit()
        finally:
            if cur:
                if not sansTran:
                    self._dbconnection.rollback()
        return result

    
    @keyword(name=None, tags=("Query",))
    def call_stored_procedure(self, spName, spParams=None, sansTran=False):
        """
        *Uses the inputs of `spName` and 'spParams' to call a stored procedure.* The return from this keyword will always be a list.
        
        *Arguments*

        ``spName``: Name of stored procedure
        
        ``spParams``: List of parameters being sent in. The list can be one or multiple items.

        ``sansTran``: Optional. Set `sansTran` to True to run command without an explicit transaction commit or rollback.
        
        *Examples*

        | @{ParamList} = | Create List | FirstParam | SecondParam | ThirdParam |
        | @{QueryResults} = | `Call Stored Procedure` | DBName.SchemaName.StoredProcName | List of Parameters |

        | @{ParamList} = | Create List | Testing | LastName |
        | Set Test Variable | ${SPName} = | DBTest.DBSchema.MyStoredProc |
        | @{QueryResults} = | `Call Stored Procedure` | ${SPName} | ${ParamList} |
        | Log List | @{QueryResults} |

        Using optional `sansTran` to run command without an explicit transaction commit or rollback:
        | @{QueryResults} = | `Call Stored Procedure` | DBName.SchemaName.StoredProcName | List of Parameters | True |
        """
        if spParams is None:
            spParams = []
        cur = None
        try:
            if self.db_api_module_name in ["cx_Oracle"]:
                cur = self._dbconnection.cursor()
            else:
                cur = self._dbconnection.cursor(as_dict=False)
            PY3K = sys.version_info >= (3, 0)
            if not PY3K:
                spName = spName.encode('ascii', 'ignore')
            logger.info('Executing : Call Stored Procedure  |  %s  |  %s ' % (spName, spParams))
            cur.callproc(spName, spParams)
            cur.nextset()
            retVal=list()
            for row in cur:
                #logger.info ( ' %s ' % (row))
                retVal.append(row)
            if not sansTran:
                self._dbconnection.commit()
            return retVal
        finally:
            if cur:
                if not sansTran:
                    self._dbconnection.rollback()

    def __execute_sql(self, cur, sqlStatement):
        return cur.execute(sqlStatement)
