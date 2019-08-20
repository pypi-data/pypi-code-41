from random import shuffle
import numpy as np

from .diversity import shannon_diversity, lottery_shannon
from .groups import group_submatrix


def null_dists_comp(data, groups, nullSize):
    # data is a 2d array of all the numerical data of species across samples
    # from the input file. groups is a list of the groups that each species
    # belongs to taken from the final column of the inpt file.
    # nullSize is how many rows of null data are in the final array.
    # Returns a list containing the null distributions of all groups
    # for comp scores.
    uniqueGroups = np.unique(groups)
    nullDists = np.empty((len(uniqueGroups), nullSize, data.shape[1]))

    for i in range(len(uniqueGroups)):
        group = uniqueGroups[i]
        nullDists[i] = null_dist_comp(data, groups, group, nullSize)
    return nullDists


def null_dist_comp(data, groups, group, nullSize):
    # data is a 2d array of all the numerical data of species across samples
    # from the input file. groups is a list of the groups that each species
    # belongs to taken from the final column of the inpt file.
    # group is an element of groups and is the specific group that a null dist
    # will be generated for. nullSize is how many rows of null data are
    # in the final array.
    # Creates a null distribution of a group by shuffling groups
    # nullSize times and calculating the shannon diversity of the
    # shuffled groups

    nullDist = np.empty((nullSize, data.shape[1]))
    shuffledGroups = groups.copy()  # Creating a copy to shuffle in place
    for i in range(nullSize):
        shuffle(shuffledGroups)
        groupSubmatrix = group_submatrix(data, shuffledGroups, group)
        nullDist[i] = np.array(shannon_diversity(groupSubmatrix))
    return nullDist


def null_dist_lottery(groupSubmatrix, nullSize):
    # groupSubmatrix is a 2d array of numerical data of species across samples
    # for a specific group. nullSize is how many rows of null data are
    # in the final array.
    # Creates a null distribution of a lottery group by shuffling each column
    # of a group nullSize times and calculating the shannon diversity of the
    # row sum

    # Creating an empty copy of groupSubmatrix (same dimensions)
    nullDist = np.empty((nullSize, groupSubmatrix.shape[1]))

    for i in range(nullSize):
        # Creating an empty array the size of the submatrix
        shuffledGroup = np.empty(groupSubmatrix.shape, dtype=int)
        for x in range(groupSubmatrix.shape[1]):
            # Splicing the xth column
            column = groupSubmatrix[0:, x].copy()
            shuffle(column)

            # Place column back in a new matrix
            shuffledGroup[:, x] = column

        shannonArray = np.array(lottery_shannon(shuffledGroup))
        nullDist[i] = shannonArray

    return nullDist


def null_dists_lottery(data, groups, nullSize):
    # data is a 2d array of all the numerical data of species across samples
    # from the input file. groups is a list of the groups that each species
    # belongs to taken from the final column of the inpt file.
    # nullSize is how many rows of null data are in the final array.
    # Returns a list containing the null distributions of all groups
    # for lot scores.

    uniqueGroups = np.unique(groups)
    nullDists = np.empty((len(uniqueGroups), nullSize, data.shape[1]))

    for i in range(len(uniqueGroups)):
        group = uniqueGroups[i]
        nullDists[i] = null_dist_lottery(group_submatrix(data, groups, group),
                                         nullSize)
    return nullDists
