import numpy as np
import pandas as pd
from typing import List, Any
from drdigit.digit_entropy_distribution import (
    prob_of_entr, get_entropy,
    _DEFAULT_PE_RANDOM_SEED, _DEFAULT_PE_ITERATIONS
)
from drdigit.twin_digits import prob_of_twins
from drdigit.digit_correlations import equality_prob_vector


def _get_overhearing_scores(group_ids: List[Any],
                            base_columns: List[List[int]],
                            indep_columns: List[List[int]]) -> None:

    indep_colnames = ["col_%d" % i for i in range(len(indep_columns))]
    indep_dict = {
        indep_colname: col
        for col, indep_colname in zip(indep_columns, indep_colnames)
    }

    dfs = [
        pd.DataFrame(dict(base=base, group_id=group_ids, **indep_dict))
        for base in base_columns
    ]

    def equality_prob_coeff_vector_df(df):
        return pd.Series(equality_prob_vector(df["base"],
                                              [df[colname]
                                              for colname in indep_colnames]))

    def geom_mean(x):
        return np.prod(x) ** (1 / len(x))

    coeff_dfs = []
    for df in dfs:
        coeff_df = df.groupby(["group_id"]).apply(equality_prob_coeff_vector_df)
        coeff_dfs.append(coeff_df)

    concatenated_df = pd.concat(coeff_dfs, axis=1)

    return concatenated_df.apply(geom_mean, axis=1)


def get_group_scores(group_ids: List[Any], digits: List[int],
                     overhearing_base_columns: List[List[int]]=[],
                     overhearing_indep_columns: List[List[int]]=[],
                     seed: int=_DEFAULT_PE_RANDOM_SEED,
                     iterations: int=_DEFAULT_PE_ITERATIONS,
                     quiet: bool=False) -> pd.Series:
    """
    Generate a series of scores about the 10 base digit groups defined by the
    parameters. The score is proportionate with probabilities of certain
    properties of the individual digit groups conditional on uniform digit
    distribution, for instance a score of 1 tells that the digit group looks
    very ordinary in the examined respects.

    :param group_ids: Array-like defining which group contains the digit at the
        matching index in digits. E.g. this could be a municipality identifier.
    :param digits: Digits of the groups to examine. It could be the last digit
        of per ward election vote counts.
    :param overhearing_base_columns: Columns with last digit distributions which
        can be considered/should be uniform.
    :param overhearing_indep_columns: Columns with last digits that should be
        independent from the base columns.
    :param seed: Random seed for MC simulations yielding CDFs.
    :param iterations: Number of iterations for MC simulations.
    :param quiet: Whether to suppress messages.
    :return: The series of scores, indexed by the group IDs.
    """

    # TODO: can add seeds instead of a shared seed
    def agg_prob_of_entr(x: List[int]):
        return prob_of_entr(len(x), get_entropy(x),
                            seed=seed, iterations=iterations,
                            quiet=quiet)

    df = pd.DataFrame(dict(group_id=group_ids, digit=digits))
    agg = df.groupby(["group_id"]).aggregate([agg_prob_of_entr, prob_of_twins])

    if len(overhearing_base_columns) > 0 and len(overhearing_indep_columns) > 0:
        overhearing_scores = get_overhearing_scores(
            group_ids,
            overhearing_base_columns,
            overhearing_indep_columns,
        )

        agg["overhearing_prob"] = overhearing_scores

    agg = agg.apply(np.prod, axis=1)
    # TOOD: is it really a series?
    return agg


if __name__ == "__main__":
    print(get_group_scores([0, 0, 0, 0,
                            1, 1],
                           [5, 6, 3, 6,
                            5, 5]))
    print(_get_overhearing_scores(
        group_ids=[1, 1, 2, 2],
        base_columns=[[1, 2, 3, 4]],
        indep_columns=[[2, 3, 3, 4], [10, 11, 11, 10]],
    ))
