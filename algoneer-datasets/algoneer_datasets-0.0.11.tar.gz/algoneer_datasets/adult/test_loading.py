from . import load_dataset
from algoneer import Dataset, Project
import pandas as pd

def test_loading():
    project = Project("test")
    ds = load_dataset(project)
    assert isinstance(ds, Dataset)
    df = ds.df
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 32561
    assert len(df.columns) == 0