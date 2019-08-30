from algoneer.dataset.pandas import PandasDataset
import os

path = os.path.dirname(__file__)

def load_dataset():
    ds = PandasDataset.from_path(path)
    return ds
