import pandas as pd

def save_dataframe(df, file_name):
    df.to_csv(file_name, encoding='utf-8', index=False)

def read_dataframe(file_name):
    return pd.read_csv(file_name)