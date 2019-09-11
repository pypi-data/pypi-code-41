#!/usr/bin/env python3
#===============================================================================
# coloc.py
#===============================================================================

# Imports ======================================================================

import math
import sumstats




# Functions ====================================================================

def coloc(
    trait1_lnbfs,
    trait2_lnbfs,
    prior1: float = 1e-4,
    prior2: float = 1e-4,
    prior12: float = 1e-5
):
    """Perform a Bayesian colocalization test (with two traits)

    Parameters
    ----------
    trait1_lnbfs
        sequence of log Bayes factors for the first trait
    trait2_lnbfs
        sequence of log Bayes factors for the second trait
    prior1
        first prior parameter for the colocalization model [1e-4]
    prior2
        second prior parameter for the colocalization model [1e-4]
    prior12=1e-5
        third prior parameter for the colocalization model [1e-5]
    
    Returns
    -------
    generator
        posterior probabilities for the five colocalization hypotheses
    """

    log_numerators = (
        0,
        math.log(prior1) + sumstats.log_sum(trait1_lnbfs),
        math.log(prior2) + sumstats.log_sum(trait2_lnbfs),
        math.log(prior1) + math.log(prior2) + sumstats.log_sum(
            trait1_lnbf + trait2_lnbf
            for i, trait1_lnbf in enumerate(trait1_lnbfs)
            for j, trait2_lnbf in enumerate(trait2_lnbfs)
            if i != j
        ),
        math.log(prior12) + sumstats.log_sum(
            trait1_lnbf + trait2_lnbf
            for trait1_lnbf, trait2_lnbf in zip(trait1_lnbfs, trait2_lnbfs)
        )
    )
    return (
        math.exp(log_numerator - sumstats.log_sum(log_numerators))
        for log_numerator in log_numerators
    )


def two_indep_assoc_numerator(lnbfs1, lnbfs2, prior1, prior2):
    return math.log(prior1) + math.log(prior2) + sumstats.log_sum(
        lnbf1 + lnbf2
        for i, lnbf1 in enumerate(lnbfs1)
        for j, lnbf2 in enumerate(lnbfs2)
        if i != j
    )


def three_indep_assoc_numerator(lnbfs1, lnbfs2, lnbfs3, prior1, prior2, prior3):
    return (
        math.log(prior1)
        + math.log(prior2)
        + math.log(prior3)
        + sumstats.log_sum(
            lnbf1 + lnbf2 + lnbf3
            for i, lnbf1 in enumerate(lnbfs1)
            for j, lnbf2 in enumerate(lnbfs2)
            for k, lnbf3 in enumerate(lnbfs3)
            if not any((i == j, j == k, i == k))
        )
    )


def moloc(
    trait1_lnbfs,
    trait2_lnbfs,
    trait3_lnbfs,
    prior1: float = 1e-4,
    prior2: float = 1e-4,
    prior3: float = 1e-4,
    prior12: float = 1e-6,
    prior23: float = 1e-6,
    prior13: float = 1e-6,
    prior123: float = 1e-7,
):
    """Perform a Bayesian colocalization test (with three traits)

    Parameters
    ----------
    trait1_lnbfs
        sequence of log Bayes factors for the first trait
    trait2_lnbfs
        sequence of log Bayes factors for the second trait
    trait2_lnbfs
        sequence of log Bayes factors for the third trait
    prior1
        first prior parameter for the colocalization model [1e-4]
    prior2
        second prior parameter for the colocalization model [1e-4]
    prior3
        second prior parameter for the colocalization model [1e-4]
    prior12=1e-5
        third prior parameter for the colocalization model [1e-5]
    prior13=1e-5
        third prior parameter for the colocalization model [1e-5]
    prior23=1e-5
        third prior parameter for the colocalization model [1e-5]
    prior123=1e-5
        third prior parameter for the colocalization model [1e-5]
    
    Returns
    -------
    generator
        posterior probabilities for the 15 colocalization hypotheses
    """

    trait12_lnbfs = tuple(
        lnbf1 + lnbf2 for lnbf1, lnbf2 in zip(trait1_lnbfs, trait2_lnbfs)
    )
    trait23_lnbfs = tuple(
        lnbf2 + lnbf3 for lnbf2, lnbf3 in zip(trait2_lnbfs, trait3_lnbfs)
    )
    trait13_lnbfs = tuple(
        lnbf1 + lnbf3 for lnbf1, lnbf3 in zip(trait1_lnbfs, trait3_lnbfs)
    )
    trait123_lnbfs = tuple(
        lnbf1 + lnbf2 + lnbf3
        for lnbf1, lnbf2, lnbf3 in zip(trait1_lnbfs, trait2_lnbfs, trait3_lnbfs)
    )
    log_numerators = (
        0, # H0
        math.log(prior1) + sumstats.log_sum(trait1_lnbfs), # H1
        math.log(prior2) + sumstats.log_sum(trait2_lnbfs), # H2
        math.log(prior3) + sumstats.log_sum(trait3_lnbfs), # H3
        math.log(prior12) + sumstats.log_sum(trait12_lnbfs), # H4
        math.log(prior23) + sumstats.log_sum(trait23_lnbfs), # H5
        math.log(prior13) + sumstats.log_sum(trait13_lnbfs), # H6
        two_indep_assoc_numerator(trait1_lnbfs, trait2_lnbfs, prior1, prior2), # H7
        two_indep_assoc_numerator(trait2_lnbfs, trait3_lnbfs, prior2, prior3), # H8
        two_indep_assoc_numerator(trait1_lnbfs, trait3_lnbfs, prior1, prior3), # H9
        two_indep_assoc_numerator(trait1_lnbfs, trait23_lnbfs, prior1, prior23), # H10
        two_indep_assoc_numerator(trait3_lnbfs, trait12_lnbfs, prior3, prior12), # H11
        two_indep_assoc_numerator(trait2_lnbfs, trait13_lnbfs, prior2, prior13), # H12
        three_indep_assoc_numerator( # H13
            trait1_lnbfs, trait2_lnbfs, trait3_lnbfs, prior1, prior2, prior3
        ),
        math.log(prior123) + sumstats.log_sum(trait123_lnbfs) # H14
    )
    return (
        math.exp(log_numerator - sumstats.log_sum(log_numerators))
        for log_numerator in log_numerators
    )


def ascii_bar(prob: float):
    """Draw an ascii bar to display a probability

    Parameters
    ----------
    prob
        the probability value to display
    
    Returns
    -------
    string
        the ascii bar
    """
    level = int(prob * 20)
    return '[{}{}]'.format('|' * int(level), ' ' * (20-level))


def print_coloc_result(
    title: str,
    pp0: float,
    pp1: float,
    pp2: float,
    pp3: float,
    pp4: float
):
    """Print an ascii representation of the colocalization test result

    Parameters
    ----------
    title
        a title for the ascii art
    pp0
        the posterior probability of H0: no association
    pp1
        the posterior probability of H1: association in trait 1 only
    pp2
        the posterior probability of H2: association in trait 2 only
    pp3
        the posterior probability of H3: independent associations
    pp4
        the posterior probability of H4: colocalized associations
    """
    
    print(
        '\n'.join(
            ('', title, '') + tuple(
                'PP{}: {} [ {} ]'.format(i, ascii_bar(pp), pp)
                for i, pp in enumerate((pp0, pp1, pp2, pp3, pp4))
            )
            + ('',)
        )
    )
