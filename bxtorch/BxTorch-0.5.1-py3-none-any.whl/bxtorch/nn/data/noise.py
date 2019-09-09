#
#  nn/data/noise.py
#  bxtorch
#
#  Created by Oliver Borchert on May 19, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

from torch.utils.data import IterableDataset
import bxtorch.nn.functional as X

class NoiseDataset(IterableDataset):
    """
    Infinite dataset for generating noise from a given probability distribution.
    Can e.g. be used with Generative Adversarial Networks.
    """

    # MARK: Initialization
    def __init__(self, noise_type, dimension):
        """
        Initializes a new dataset with the given noise type.

        Parameters:
        -----------
        - noise_type: str
            The noise type to use.
        - dimension: int
            The dimension of the noise to generate.
        """
        super().__init__()

        self.noise_type = noise_type
        self.dimension = dimension

    # MARK: Special Methods
    def __iter__(self):
        # We do not need to consider single- or multi-process data loading since
        # the noise is randomly sampled anyway
        return self._generator_func(self.noise_type, self.dimension)

    # MARK: Private Methods
    def _generator_func(self, noise_type, dimension):
        while True:
            yield X.generate_noise([dimension], noise_type)
            