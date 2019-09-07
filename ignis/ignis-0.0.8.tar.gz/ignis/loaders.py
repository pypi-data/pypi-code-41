from torch.utils import data
from .datasets import Dataset


def create_loaders(x,
                   y,
                   validation_split=0,
                   batch_size=16,
                   num_workers=6,
                   ):
    dataset = Dataset(x=x, y=y)

    x_size = len(x)
    validation_size = int(x_size * validation_split)
    train_size = x_size - validation_size
    train_set, validation_set = data.random_split(dataset=dataset, lengths=(train_size, validation_size))

    train_loader = data.DataLoader(
        dataset=train_set,
        batch_size=batch_size,
        num_workers=num_workers,
    )
    validation_loader = data.DataLoader(
        dataset=validation_set,
        batch_size=batch_size,
        num_workers=num_workers,
    )

    return train_loader, validation_loader
