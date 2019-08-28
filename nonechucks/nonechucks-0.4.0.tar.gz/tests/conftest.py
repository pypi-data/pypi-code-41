import pytest

from torch.utils.data import Dataset


class NumbersDataset(Dataset):
    def __init__(self, size, bad_indices=None, exception_cls=RuntimeError):
        self.size = size
        self.bad_indices = bad_indices if bad_indices else []
        self.exception_cls = exception_cls

        self.data = list(range(self.size))

    def __len__(self):
        return self.size

    def __getitem__(self, idx):
        if idx in self.bad_indices:
            raise self.exception_cls("Bad sample")
        return self.data[idx]


@pytest.fixture
def safe_dataset():
    dataset = NumbersDataset(20)
    return dataset
