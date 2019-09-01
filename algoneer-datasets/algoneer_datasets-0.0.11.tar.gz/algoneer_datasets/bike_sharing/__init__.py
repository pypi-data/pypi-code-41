from algoneer import Project
from algoneer.dataset.pandas import PandasDataset
import os

path = os.path.dirname(__file__)

def load_dataset(project: Project) -> PandasDataset:
    ds = PandasDataset.from_path(project, path)
    return ds
