import mysql.connector
from mysql.connector import Error
import os
import pandas as pd
import re
import numpy as np
import warnings

from typing import List, Tuple


def connect_and_query(query: str) -> pd.DataFrame:
    """
    Opens a connection to a SQL database and returns the output the Query as a pandas DataFrame
    It is important to note that the environment variables need to be set prior to execution. 

    Args:
        query (str): The query to be fetched at the database.

    Returns:
        (:class:`pandas.Dataframe`): The output of the query in DataFrame format.
    """
    mySQLconnection = None
    # for the next part, it is important to set the environment variables
    try:
        print("Opening MySQL Connection")
        mySQLconnection = mysql.connector.connect(
            host=os.environ.get("HOST_PLM_DATABASE"),
            database=os.environ.get("PLM_DATABASE"),
            user=os.environ.get("USER_PLM_DATABASE"),
            password=os.environ.get("PASSWORD_PLM_DATABASE"),
        )
        print("Connection Opened, starting Fetch")

        output = pd.read_sql(query, con=mySQLconnection)

    except Error as e:
        print("Error while connecting to MySQL", e)
        return e

    finally:
        # closing database connection.
        if mySQLconnection:
            if mySQLconnection.is_connected():
                mySQLconnection.close()
                print("MySQL connection is closed")
                return output


def format_produto_animale(produto: str) -> str:
    """
    Formats the 'produto' column to follow a xx.xx.x+ standard, thus removing forbidden characters (letters, specials, etc).

    Args:
        produto (str): A single entry from the produto column.

    Returns:
        (str): The formatted string if it fits the pattern. If no match is found returns nothing (empty string)

    """
    m = re.match("(^[0-9]{2}\.[0-9]{2}\.[0-9]+)", produto)
    if m:
        return m.groups()[0]
    else:
        return produto


def calculate_giro(
    df: pd.DataFrame, columns: list = ["value", "qtde", "preco", "qtty"]
) -> pd.DataFrame:
    """
    Calculates giro and disc from a dataframe

    Args:
        df (:class:`pandas.Dataframe`):: A correctly structured DataFrame
        columns (list(str)): The column names that represent:
            - value
            - qtde
            - preco
            - qtty
    
    Returns:
        (:class:`pandas.Dataframe`):: The original DataFrame with two additional columns,
        giro and discount.
    
    Todo:
        Complete the Args documentation.
    """
    # columns[0] = value, columns[1] = qtde, columns[2] = preco_varejo_original, columns[3] = qtty
    nan_indexes = []

    # checking if any important row has a zero (dividend row)
    for c in columns:
        if c == columns[0]:
            pass
        else:
            if df[c].eq(0).any().sum() > 0:
                column_indexes = np.where(df[columns[1]].eq(0).tolist())[0].tolist()
                nan_indexes = nan_indexes + column_indexes
                warnings.warn(
                    "{} column has at least one 0, resulting in NaN.".format(c)
                )

    warnings.warn("The NaN indexes are: {}".format(np.unique(nan_indexes)))

    # calculating giro
    df["giro"] = df[columns[0]] / (df[columns[1]] * df[columns[2]])
    # calculating discount
    df["disc"] = 1 - df[columns[0]] / (df[columns[3]] * df[columns[2]])

    return df


def clean_animale_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
        Cleans the animale sales dataset.

        It excludes infinite, zero quantities and NaN entries from the DataFrame.

        Args:
            df (:class:`pandas.Dataframe`): The animale sales dataset.

        Returns:
           :class:`pandas.Dataframe`: The cleaned dataset.
    """
    df.drop_duplicates(subset="id_produto_cor", keep=False, inplace=True)
    df["qtde"].replace(0, np.nan, inplace=True)
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def load_provao_dataset(
    path_animale: str, path_provao: str
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
        Loads the animale sales dataset (with sales indicators) and the votes dataset.

        Args:
            path_animale (str): Path to the animale dataset in Pickle format.
            path_provao (str): Path to the provao dataset in CSV format.
        
        Returns:
            (tuple): Tuple contaning:
                - df_merged (:class:`pandas.Dataframe`): A merged dataset from animale and provao.
                - df_animale (:class:`pandas.Dataframe`): Animale sales dataset.
                - df_provao (:class:`pandas.Dataframe`): Provao dataset      
    """

    df_animale = pd.read_pickle(path_animale)
    df_provao = pd.read_csv(path_provao)

    df_provao = df_provao.rename(columns={"preco": "nota_preco"})
    df_provao.drop(columns=["id_colecao", "id_produto_estilo", "produto"], inplace=True)

    df_animale = clean_animale_dataset(df_animale)
    df_animale.rename(columns={"preco_varejo_original": "preco"}, inplace=True)

    df_merged = df_animale.merge(df_provao, on="id_produto_cor")
    return df_merged, df_animale, df_provao


def reorganize_tags(tags: pd.DataFrame) -> pd.DataFrame:
    """
        Fixes the unorganized tags from the database, separating by 
        category.
    
        The value from the category is determined by the first uppercase
        letter.

        Args:
            tags (:class:`pandas.Dataframe`): 
        Returns:
            :class:`pandas.Dataframe`: The tags organized by category.

    """
    output = tags.copy
    output = tags.loc[:, []]
    for col in tags:
        for cat in tags[col].unique():
            if cat:
                aux = tags[tags[col] == cat][col]
                new_col = re.findall("([a-z]*)(.*)", cat)
                # Category value starts at the first uppercase letter.
                if new_col:
                    category_value = new_col[0][1]
                    new_col = new_col[0][0]
                    if new_col not in output.columns:
                        output[new_col] = None
                    output.loc[aux.index, new_col] = category_value
    return output


def label_encode_col(col):
    """
        Encodes a :class:`pandas.Series` with a label encoder that 
        accepts missing values (codified as a "None" string)

        Args:
            col (:class:`pandas.Series`): A column from a dataframe that 
            can include a missing entry codified as "None".
        Returns:
            :class:`pandas.Series`: The label-encoded column, with "None" 
            codified with label 0.
    """

    unique_values = col.unique()
    if "None" not in unique_values:
        unique_values = np.insert(unique_values, 0, "None")
    mapping_dict = {key: value for (value, key) in enumerate(unique_values)}
    reverse_dict = {key: value for (key, value) in enumerate(unique_values)}

    if "None" in mapping_dict:
        none_class = mapping_dict["None"]
        zero_key = reverse_dict[0]
        mapping_dict[zero_key], mapping_dict["None"] = (none_class, 0)

    # print(mapping_dict)
    return col.apply(lambda x: mapping_dict[x])

def insertData (table, data, try_num = 0, update_set = {}):
    """
    Opens a connection to a SQL database and inserts the received Dataframe or Series into the received Table
    It is important to note that the environment variables need to be set prior to execution. 

    Args:
        table (str): Table where data will be inserted.
        data (:class:`pandas.Dataframe` or :class:`pandas.Series`): Data to be inserted. Column names must match table columns.
        update_set (set): Set with columns to update with ON DUPLICATE KEY clause.
        
    Returns:
        (list): List of inaerted ids.
    """
    try:
        print("Opening MySQL Connection")
        mySQLconnection = mysql.connector.connect(
            host=os.environ.get("HOST_PLM_DATABASE"),
            database=os.environ.get("PLM_DATABASE"),
            user=os.environ.get("USER_PLM_DATABASE"),
            password=os.environ.get("PASSWORD_PLM_DATABASE"),
        )
        print("Connection Opened, starting Insert")

    except Error as e:
        print("Error while connecting to MySQL", e)
        return e

    cursor = mySQLconnection.cursor()
    if (type(data) == pd.core.series.Series):
        data = data.sort_index()
        myDict = data.to_dict()
        tuples = [tuple([val for idx, val in data.iteritems()])]
    else:
        data = data.reindex(sorted(data.columns), axis=1)
        myDict = data.to_dict(orient='records')[0]
        tuples = [tuple(x) for x in data.values]

    sql = "INSERT INTO " + table + " (" + ', '.join(sorted(myDict.keys())) + ") VALUES (" + ', '.join(['%s'] * len(myDict)) + ")"
    if (len(update_set) > 0):
        upd_str = ""
        for value in update_set:
            upd_str = upd_str + value + " = VALUES(" + value + "), "
        upd_str = upd_str[:-2] + ";"
        sql = sql + " ON DUPLICATE KEY UPDATE " + upd_str
    print (sql)
    
    try:
        cursor.executemany(sql, tuples)
        mySQLconnection.commit()
        print (cursor.lastrowid)
        ids = [cursor.lastrowid + i for i in range(cursor.rowcount)]
        cursor.close()
        mySQLconnection.close()

    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        mySQLconnection.rollback()
        if (try_num > 10):
            cursor.close()
            mySQLconnection.close()
            return False
        else:
            print ("Error, trying for the " + str(try_num + 1) + ' time.') 
            cursor.close()
            mySQLconnection.close()
            return insertData(table, data, try_num + 1)

    return ids