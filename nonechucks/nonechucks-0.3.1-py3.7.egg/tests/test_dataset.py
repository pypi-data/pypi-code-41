import logging
import pytest

import nonechucks as nc
from tests.conftest import NumbersDataset


logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "size, bad_indices", [(3, [2]), (20, []), (20, [1, 2, 3]), (0, [])]
)
def test_is_index_built(size, bad_indices):
    dataset = NumbersDataset(size, bad_indices=bad_indices)
    safe_dataset = nc.SafeDataset(dataset)

    assert safe_dataset.is_index_built is False
    for i in safe_dataset:
        pass
    assert safe_dataset.is_index_built is True


@pytest.mark.parametrize("size, bad_indices", [])
def test_num_samples_examined():
    pass


@pytest.mark.parametrize()
def test_getitem():
    pass
