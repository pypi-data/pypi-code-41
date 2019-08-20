import torch
import numpy


class Dataset(torch.utils.data.Dataset):
    """Characterizes a dataset for PyTorch"""
    def __init__(self, x, y):
        """Initialization"""
        if not isinstance(x, numpy.ndarray) and not isinstance(x, torch.Tensor):
            raise Exception('Only numpy arrays and torch tensors are allowed as input data')
        if not isinstance(y, numpy.ndarray) and not isinstance(y, torch.Tensor):
            raise Exception('Only numpy arrays and torch tensors are allowed as input data')

        if isinstance(x, numpy.ndarray):
            self.x = torch.from_numpy(x).float()
        else:
            self.x = x.float()

        if isinstance(y, numpy.ndarray):
            self.y = torch.from_numpy(y).float()
        else:
            self.y = y.float()

    def __len__(self):
        """Denotes the total number of samples"""
        return len(self.x)

    def __getitem__(self, index):
        """Generates one sample of data"""
        x = self.x[index]
        y = self.y[index]

        return x, y