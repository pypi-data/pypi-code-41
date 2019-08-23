import pytest
from drdigit import LodigeTest


@pytest.mark.entropy
def test_slices():
    res = list(LodigeTest.get_slice_limits([1, 2, 2, 3, 3, 3]))
    assert (
        res ==
            [(0, 1),
             (1, 3),
             (3, 6)]
    )
