from drdigit.twin_digits import prob_of_twins


def test_prob_of_twins():
    assert prob_of_twins([1, 1]) < prob_of_twins([1, 2])
    assert prob_of_twins([1, 1, 2, 3, 4, 5]) == \
           prob_of_twins([1, 1, 2, 3, 4, 5])
    assert prob_of_twins([1, 2]) == prob_of_twins([2, 1])
    assert prob_of_twins([1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]) > \
           prob_of_twins([1, 1, 2, 2, 3, 4, 5, 6, 7, 8, 9])
