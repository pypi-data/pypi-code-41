import pytest
from drdigit.twin_digits import prob_of_twins


@pytest.mark.correlations
def test_prob_of_correlations_props():
    pass
    # assert prob_of_twins([1, 1]) < prob_of_twins([1, 2])
    # assert prob_of_twins([1, 1, 2, 3, 4, 5]) == \
    #        prob_of_twins([1, 1, 2, 3, 4, 5])
    # assert prob_of_twins([1, 2]) == prob_of_twins([2, 1])
    # assert prob_of_twins([1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]) > \
    #        prob_of_twins([1, 1, 2, 2, 3, 4, 5, 6, 7, 8, 9])


@pytest.mark.correlations
def test_prob_of_twins_values():
    assert prob_of_twins([1, 1]) == pytest.approx(0.1, 1e-10)
    assert prob_of_twins([1, 1, 1, 1]) == pytest.approx(0.001, 1e-10)



"""

if __name__ == "__main__":
    # cdf = digit_correlation_cdf(8531)
    # print("probability correlations higher than 0.01985", 1 - cdf(0.01985))
    # cdf = digit_equality_prob_mc_cdf(8531)
    # print("nonparam. probability equalities higher than 0.11", 1 - cdf(0.11))
    # cdf2 = digit_equality_prob_analytical_cdf(8531)
    # for i in range(100):
    #     x = cdf2(0.11)
    # print("param. probability equalities higher than 0.11", 1 - cdf2(0.11))

    rel_freq = equality_rel_freq(
        np.array([1, 2]),
        np.array([1, 2])
    )
    assert(rel_freq == 1.0)

    rel_freq = equality_rel_freq(
        np.array([1, 2]),
        np.array([1, 0])
    )
    assert(rel_freq == 0.5)

    cdf = digit_equality_prob_cdf(2)
    # P(rel_req=1, i.e. at least 2 matches out of 2) = 0.1 ^ 2
    assert(abs(cdf(1) - 0.01) < 0.0001)

    vec = equality_prob_vector(
        base_column=np.array([1, 2]),
        indep_columns=[np.array([1, 2]), np.array([1, 3]), np.array([10, 11])],
    )

    assert(sum(abs(vec - np.array([0.01, 0.19, 1.0]))) < 0.0001)


"""
