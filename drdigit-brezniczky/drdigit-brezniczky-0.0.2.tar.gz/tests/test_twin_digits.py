import pytest
from drdigit.twin_digits import prob_of_twins


@pytest.mark.twins
def test_prob_of_twins_props():
    assert prob_of_twins([1, 1]) < prob_of_twins([1, 2])
    assert prob_of_twins([1, 1, 2, 3, 4, 5]) == \
           prob_of_twins([1, 1, 2, 3, 4, 5])
    assert prob_of_twins([1, 2]) == prob_of_twins([2, 1])
    assert prob_of_twins([1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]) > \
           prob_of_twins([1, 1, 2, 2, 3, 4, 5, 6, 7, 8, 9])


@pytest.mark.twins
def test_prob_of_twins_values():
    assert prob_of_twins([1, 1]) == pytest.approx(0.1, 1e-10)
    assert prob_of_twins([1, 1, 1, 1]) == pytest.approx(0.001, 1e-10)
