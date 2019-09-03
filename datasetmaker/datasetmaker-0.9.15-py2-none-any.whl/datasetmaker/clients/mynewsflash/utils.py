import os
import pandas as pd


def get_abspath(path):
    """Returns the absolute path to path data"""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(root, 'data')
    return os.path.join(data_dir, path)


def stretch(df, col):
    """Given a single column with comma-separated values, or regular Python
    lists, take each unique value and duplicate the row with that value in col.

    """
    if isinstance(df[col].dropna().iloc[0], str):
        df[col] = df[col].str.split(',', expand=False)
    max_entries = df[col].apply(len).max()
    df = pd.concat([df, df[col].apply(lambda x: pd.Series(x))], axis=1)
    df = df.drop(col, axis=1)
    id_vars = df.columns[:-max_entries]
    value_vars = df.columns[-max_entries:]
    df = pd.melt(df, id_vars=id_vars, value_vars=value_vars)
    df = df.drop('variable', axis=1)
    df = df.rename(columns={'value': col})
    df = df.dropna(subset=[col])

    return df


def balance_tags(df, tag_col='cat'):
    """Downsamples a dataframe so that each category
    contains as many samples as the smallest one.

    Parameters
    ----------

    df : pd.DataFrame
        Dataframe with tagged items.
    tag_col : str
        Name of column with class labels.
    """

    floor = df[tag_col].value_counts().min()
    resampled = []
    for tag in df[tag_col].unique():
        sub = df[df[tag_col] == tag]
        resampled.append(sub.sample(floor))
    return pd.concat(resampled)
