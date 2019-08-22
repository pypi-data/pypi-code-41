import tensorflow as tf
from tensorflow import keras
import pandas as pd


def plot_history(history, contains, skip=0):
    df = pd.DataFrame(history.history)
    df[list(df.filter(regex=contains))].iloc[skip:].plot()


def categorical_fit_transform(df, cat_cols):
    df = df.copy()
    cat_features_map = {}
    df[cat_cols] = df[cat_cols].astype("category")
    for cat_col in cat_cols:
        cat_features_map[cat_col] = dict(enumerate(df[cat_col].cat.categories, start=1))
        df[cat_col] = df[cat_col].cat.codes + 1
    return df, cat_features_map


def categorical_transform(df, cat_features_map):
    df = df.copy()
    for cat_col in cat_features_map:
        df[cat_col] = df[cat_col].map(
            {value: key for key, value in cat_features_map[cat_col].items()}
        )
        df[cat_col].fillna(value=0, inplace=True)
        df[cat_col] = df[cat_col].astype(int)
    return df


def continuous_fit_transform(df, cont_cols):
    df = df.copy()
    cont_features_map = {}
    df[cont_cols] = df[cont_cols].astype(float)
    for cont_col in cont_cols:
        cont_features_map[cont_col] = {
            "mean": df[cont_col].mean(),
            "std": df[cont_col].std(),
        }
        df[cont_col] = (
                           df[cont_col] - cont_features_map[cont_col]["mean"]
                       ) / cont_features_map[cont_col]["std"]
    return df, cont_features_map


def continuous_transform(df, cont_features_map):
    df = df.copy()
    for cont_col in cont_features_map:
        df[cont_col] = (
            df[cont_col] - cont_features_map[cont_col]["mean"]
        ) / cont_features_map[cont_col]["std"]
    return df
