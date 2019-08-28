import torch
import pytorch_transformers

from vtorch.common import Registrable


class Optimizer(Registrable):
    """
    Pytorch has a number of built-in activation functions.  We group those here under a common
    type, just to make it easier to configure and instantiate them ``from_params`` using
    ``Registrable``.
    """
    def step(self, closure=None):
        raise NotImplementedError


Registrable._registry[Optimizer] = {  # type: ignore
        "sgd": torch.optim.SGD,
        "adam": torch.optim.Adam,
        "adamW": pytorch_transformers.AdamW
}
