import numpy as np


def concat_examples(batch):
    x = np.array([example[0] for example in batch])
    t = np.array([example[1] for example in batch])
    return (x, t)