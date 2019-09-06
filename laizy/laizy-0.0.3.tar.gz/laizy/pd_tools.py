"""
Tools for pandas development
"""

import numpy as np
import pandas as pd
from multiprocessing import Pool
from typing import List, Union
import string
from .text_tools import preprocess_sentence

LINE = 1
COLUMN = 0


def parallelize(
    df: pd.DataFrame, func: callable, num_partitions: int, num_cores: int
):
    """Parallelize the execution of a function on a dataframe.

    The given function will receive as input a part of the input dataframe

    Args:
    -----
        - df: The dataframe to be modified
        - func: the function to be applied. It will receive a part of the
            dataframe
        - num_partitions: number of parts the original dataset will be split
        - num_cores: number of cores to use

    Requires:
        - df is a Dataframe
        - func is a callable
        - num_partitions is > 0 and is int
        - num_cores is > 0 and is int

    Returns:
        The dataframe with function applied

    """
    df_split: List = np.array_split(df, num_partitions)
    pool: Pool = Pool(num_cores)
    df = pd.concat(pool.map(func, df_split))
    pool.close()
    pool.join()
    return df


def apply(df: pd.DataFrame, func: callable, by: int = LINE):
    """Apply a function on a dataframe and return the modified one.

    Args:
        df: The given dataframe
        func: the function to apply
        by: Should we go line by line or column by column ?

    Requires:
        - df is a dataframe
        - func is a callable

    Returns:
        the modified dataframe

    """
    return df.apply(func, axis=by)


def select(
    df: pd.DataFrame, query: str, columns: Union[List[str], None] = None
):
    """Filter a dataframe from line that don't match a query string.

    Columns are filtered AFTER the selection process.
    So you can filter on columns that you will remove afterward

    Args:
        df: The dataframe
        query: A query as a string
        columns: An optionnal set of columns to keep AFTER the filtering

    Requires:
        - df is a dataframe
        - query is a valid dataframe query

    Returns:
        The filtered dataframe

    """
    if columns is not None:
        return df.query(query, engine="python")[columns]
    else:
        return df.query(query, engine="python")


def drop_selection(
    df: pd.DataFrame, query: str, columns: Union[List[str], None] = None
):
    """Drop a set of line and columns from a dataframe.

    Args:
        df: the dataframe under consideration
        query: the query for the lines to be removed
        columns: the columns to be removed

    Requires:
        - df is a dataframe
        - query is a valid dataframe query

    Returns:
        the dataframe without the lines and the columns

    """
    dropped = df.drop[select(query).index]
    columns_to_keep = dropped.columns.tolist()
    if columns is not None:
        columns_to_keep = [col for col in columns_to_keep if col not in columns]
    return dropped[columns_to_keep]


def process_column(
    df: pd.DataFrame,
    function: callable,
    column_name: str,
    modified_column_name: Union[str, None] = None,
) -> None:
    """Apply a given function to a dataframe column.

    If no new column name is given, the old one is modified

    Args:
        - df: the given dataframe
        - function: the function to be applied
        - column_name: the name of the original column
        - modified_column_name: an optionnal new column name
            If None, the old column is modified

    Requires:
        - df is a dataframe
        - function is a callable

    Effects:
        if modified_column_name is None, the original column is modified else
        a new column is created

    """
    if modified_column_name is None:
        modified_column_name = column_name

    df[modified_column_name] = df[column_name].apply(function)


def preprocess_text_column(
    df: pd.DataFrame,
    column_name: str,
    modified_column_name: Union[str, None] = None,
    should_lower: bool = True,
    should_replace_punctuation: bool = True,
    punctuation_symbols: List[str] = string.punctuation,
    punctuation_patterns: List[callable] = [
        lambda x: f" {x} ",
        lambda x: f"{x} ",
    ],
    punctuation_replace_by: str = " ",
    should_replace_special_characters: bool = True,
    special_characters: List[str] = ["\t", "\r", "\n"],
    special_replace_by: str = " ",
    should_replace_numbers: bool = False,
    numbers_replace_by: str = "0",
    should_remove_numbers: bool = False,
):
    """Preprocess a text column."""
    return process_column(
        df,
        lambda x: preprocess_sentence(
            x,
            should_lower,
            should_replace_punctuation,
            punctuation_symbols,
            punctuation_patterns,
            punctuation_replace_by,
            should_replace_special_characters,
            special_characters,
            special_replace_by,
            should_replace_numbers,
            numbers_replace_by,
            should_remove_numbers,
        ),
        column_name,
        modified_column_name=modified_column_name,
    )
