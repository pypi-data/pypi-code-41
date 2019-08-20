from math import log


def shannon_diversity(group_submatrix):
    # groupSubmatrix is a 2d array of numerical data of species across samples
    # for a specific group.
    # This function calculates the shannon_diversity for a group submatrix

    # Break the submatrix into a list of its columns
    column_list = [column(group_submatrix, i)
                   for i in range(len(group_submatrix[0]))]

    # Return a list of each columns shannon diversity for the group submatrix
    return [shannon_diversity_indv(i) for i in column_list]


def shannon_diversity_indv(group_column):
    # Returns the shannon diversity for an individual column in a group
    # H = -SUM[(pi) * ln(pi)] where pi = Number species/Number of samples
    col_sum = sum(group_column)
    if col_sum == 0:
        return 0

    pi_x_logs = []
    for y in group_column:
        pi = y/col_sum
        if pi == 0:  # log(0) = -infinity
            continue
        pi_x_logs.append(pi * log(pi))
    return -sum(pi_x_logs)


def lottery_shannon(groupSubmatrix):
    # groupSubmatrix is a 2d array of numerical data of species across samples
    # for a specific group.
    # Calculates the shannon diversity of row sums used to generate lot scores
    # Sum across rows, store in list
    summedRows = []
    for row in groupSubmatrix:
        summedRows.append(sum(row))
    # Return the Shannon diversity
    return shannon_diversity_indv(summedRows)


def column(matrix, i):
    # Returns a list made of the ith column of the matrix
    return [row[i] for row in matrix]
