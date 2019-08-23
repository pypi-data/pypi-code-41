from . import load_dataset
from algoneer import Dataset
import pandas as pd

def test_loading():
    ds = load_dataset()
    assert isinstance(ds, Dataset)
    df = ds.df
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 32561
    assert len(df.columns) == 15