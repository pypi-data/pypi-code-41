from numpy import array
import numpy


def make_3d_jagged_array(nrows, ncol):
    # nrows: array of ints, specifying the number
    # of rows to output in each subarray.
    # wrapper function that takes only one arg,
    # needed for map. y is number of cols for
    # all subarrays.
    def empty_wrapper(nrows, y=ncol): return(numpy.empty((nrows, y)))
    return list(map(empty_wrapper, nrows))


def group_submatrices(data, groups, unique):
    # data - a 2d array (D below)
    # gets colums of matrix "data" subset by each unique element within groups
    # unique - is a list of unique groups from groups.
    # This could be used to filter out specific groups,
    # say ones that don't meet the minimum group size.
    # However, for now it is equivalent to numpy.unique(groups)
    # Returns an array of the submatrix of each group
    groupSizes = [0] * len(unique)
    for i in range(len(unique)):
        groupSizes[i] = sum(groups == unique[i])

    submatrices = make_3d_jagged_array(nrows=groupSizes, ncol=len(data[0]))

    for i in range(len(unique)):
        submatrices[i] = group_submatrix(data, groups, unique[i])

    return array(submatrices)


def group_submatrix(data, groups, groupName):
    # # data is a 2d array of all the numerical data of species across samples
    # from the input file. groups is a list of the groups that each species
    # belongs to taken from the final column of the inpt file.
    # group is an element of groups and is the specific group that a submatrix
    # will be generated for.
    # Returns a 2d array of the data for a single group specified by group
    rows = (groups == groupName)
    cols = [True] * len(data[0])
    return(data[numpy.ix_(rows, cols)])
"""
def group_submatrices(data, groups, unique):
    # This function returns an array of the submatrix of each group

    Submatrices = []  # This is where we'll store the end results

    for groupName in unique:
        submatrix = group_submatrix(data, groups, groupName)
        Submatrices.append(submatrix)

    return array(Submatrices)
def group_submatrix(data, groups, groupName):
    # Returns the data for a single group specified by groupName

    submatrix = []
    # Get the submatrix where all members belong to the same group
    for i in range(data.shape[0]):
        if groupName == groups[i]:  # If the group name == that row's group
            submatrix.append(data[i])
    return array(submatrix)
"""
