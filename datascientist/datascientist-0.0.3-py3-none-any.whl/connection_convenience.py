"""
@date: 8/22/2019
@author: info@cloudframe.io
@doc: A collection of convenience functions for Data Scientists, Data Engineers, and Developers
    to read simple queries from databases into a pandas DataFrame.
"""
import os
from time import time
from datetime import datetime

import pandas as pd
import psycopg2 as ps
import cx_Oracle as cx
import mysql.connector as msc

env_dict = {
"OR_USER": ["Oracle User Name", os.environ.get("OR_USER")],
"OR_TNS": ["Oracle TNS Database Name", os.environ.get("OR_TNS")],
"OR_PASS": ["Oracle Password", os.environ.get("OR_PASS")],
"PG_USER": ["Postgres User Name", os.environ.get("PG_USER")],
"PG_DBNM": ["Postgres Database Name", os.environ.get("PG_DBNM")],
"PG_PORT": ["Postgres Port", os.environ.get("PG_PORT")],
"PG_PASS": ["Postgres Password", os.environ.get("PG_PASS")],
"PG_HOST": ["Postgres Host", os.environ.get("PG_HOST")],
"RS_USER": ["Redshift User Name", os.environ.get("RS_USER")],
"RS_DBNM": ["Redshift Database Name", os.environ.get("RS_DBNM")],
"RS_PORT": ["Redshift Port", os.environ.get("RS_PORT")],
"RS_PASS": ["Redshift Password", os.environ.get("RS_PASS")],
"RS_HOST": ["Reshift Host", os.environ.get("RS_HOST")],
"MS_USER": ["MySQL User Name", os.environ.get("MS_USER")],
"MS_DBNM": ["MySQL Database Name", os.environ.get("MS_DBNM")],
"MS_PORT": ["MySQL Port", os.environ.get("MS_PORT")],
"MS_PASS": ["MySQL Password", os.environ.get("MS_PASS")],
"MS_HOST": ["MySQL Host", os.environ.get("MS_HOST")]
}

def get_input(var_name):
    """
    @doc: Get the variable name via user input
    @args: var_name is a tuple of (plain_name, variable_value)
    @return: a str based on user input
    """
    plain_name = env_dict[var_name][0]
    ret = input("Enter a value for {}:  ".format(plain_name))
    return str(ret)

def get_pg_con():
    """
    @doc: Create a Postgres database connection
    @args: None
    @return: a psycopg2 connection object
    """
    if env_dict["PG_USER"][1] is None:
        env_dict["PG_USER"][1] = get_input("PG_USER")
        env_dict["PG_DBNM"][1] = get_input("PG_DBNM")
        env_dict["PG_PORT"][1] = get_input("PG_PORT")
        env_dict["PG_PASS"][1] = get_input("PG_PASS")
        env_dict["PG_HOST"][1] = get_input("PG_HOST")

    connection = ps.connect(dbname = env_dict["PG_DBNM"][1],
                            host = env_dict["PG_HOST"][1],
                            port = env_dict["PG_PORT"][1],
                            user = env_dict["PG_USER"][1],
                            password = env_dict["PG_PASS"][1])

    return connection

def get_rs_con():
    """
    @doc: Create a Redshift database connection
    @args: None
    @return: a psycopg2 connection object
    @note: More or less identical to the Postgres version
    """
    if env_dict["RS_USER"][1] is None:
        env_dict["RS_USER"][1] = get_input("RS_USER")
        env_dict["RS_DBNM"][1] = get_input("RS_DBNM")
        env_dict["RS_PORT"][1] = get_input("RS_PORT")
        env_dict["RS_PASS"][1] = get_input("RS_PASS")
        env_dict["RS_HOST"][1] = get_input("RS_HOST")

    connection = ps.connect(dbname = env_dict["RS_DBNM"][1],
                            host = env_dict["RS_HOST"][1],
                            port = env_dict["RS_PORT"][1],
                            user = env_dict["RS_USER"][1],
                            password = env_dict["RS_PASS"][1])

    return connection

def get_mysql_con():
    """
    @doc: Create a MySQL database connection
    @args: None
    @return: A mysql.connector connection object.
    """
    if env_dict["MS_USER"][1] is None:
        env_dict["MS_USER"][1] = get_input("MS_USER")
        env_dict["MS_DBNM"][1] = get_input("MS_DBNM")
        env_dict["MS_PORT"][1] = get_input("MS_PORT")
        env_dict["MS_PASS"][1] = get_input("MS_PASS")
        env_dict["MS_HOST"][1] = get_input("MS_HOST")

    connection = msc.connect(database = env_dict["MS_DBNM"][1],
                            host = env_dict["MS_HOST"][1],
                            port = env_dict["MS_PORT"][1],
                            user = env_dict["MS_USER"][1],
                            password = env_dict["MS_PASS"][1])

    return connection

def get_or_con():
    """
    @doc: Create an Oracle database connection
    @args: None
    @return: a cx_Oracle connection object
    """
    if env_dict["OR_USER"][1] is None:
        env_dict["OR_USER"][1] = get_input("OR_USER")
        env_dict["OR_PASS"][1] = get_input("OR_PASS")
        env_dict["OR_HOST"][1] = get_input("OR_TNS")

    con_str = "{0}/{1}@{2}".format(env_dict["OR_USER"][1],
                                   env_dict["OR_PASS"][1],
                                   env_dict["OR_TNS"][1])

    connection = cx.connect(con_str)
    return connection

def pg2df(sql, verbose = False):
    """
    @doc: create a pandas DataFrame from valid Postgres SQL
    @args: sql is a str of valid SQL
           verbose is a boolean for whether or not to print a timning message
    @return: a pandas DataFrame
    """
    con = get_pg_con()
    cur = con.cursor()
    start = time() #ts = datetime.fromtimestamp(time()).strftime("%H:%M.%S")

    cur.execute(sql)
    if verbose:
        mins = round((time() - start)/60, 2)
        print("It has taken {} minutes to execute the cursor.".format(mins))

    df = pd.DataFrame(cur.fetchall(), columns = [desc[0] for desc in cur.description])
    con.close()
    return df

def rs2df(sql, verbose = False):
    """
    @doc: create a pandas DataFrame from valid Postgres SQL
    @args: sql is a str of valid SQL
           verbose is a boolean for whether or not to print a timning message
    @return: a pandas DataFrame
    """
    con = get_rs_con()
    cur = con.cursor()
    start = time() #ts = datetime.fromtimestamp(time()).strftime("%H:%M.%S")

    cur.execute(sql)
    if verbose:
        mins = round((time() - start)/60, 2)
        print("It has taken {} minutes to execute the cursor.".format(mins))

    df = pd.DataFrame(cur.fetchall(), columns = [desc[0] for desc in cur.description])
    con.close()
    return df

def mysql2df(sql, verbose = False):
    """
    @doc: create a pandas DataFrame from valid MySQL SQL
    @args: sql is a str of valid SQL
           verbose is a boolean for whether or not to print a timning message
    @return: a pandas DataFrame
    """
    con = get_mysql_con()
    cur = con.cursor()
    start = time() #ts = datetime.fromtimestamp(time()).strftime("%H:%M.%S")

    cur.execute(sql)
    if verbose:
        mins = round((time() - start)/60, 2)
        print("It has taken {} minutes to execute the cursor.".format(mins))

    df = pd.DataFrame(cur.fetchall(), columns = [desc[0] for desc in cur.description])
    con.close()
    return df

def or2df(sql):
    """
    @doc: create a pandas DataFrame from valid Oracle SQL
    @args: sql is a str of valid SQL
           verbose is a boolean for whether or not to print a timning message
    @return: a pandas DataFrame
    """
    con = get_or_con()
    cur = con.cursor()
    start = time() #ts = datetime.fromtimestamp(time()).strftime("%H:%M.%S")

    cur.execute(sql)
    if verbose:
        mins = round((time() - start)/60, 2)
        print("It has taken {} minutes to execute the cursor.".format(mins))

    df = pd.DataFrame(cur.fetchall(), columns = [desc[0] for desc in cur.description])
    con.close()
    return df