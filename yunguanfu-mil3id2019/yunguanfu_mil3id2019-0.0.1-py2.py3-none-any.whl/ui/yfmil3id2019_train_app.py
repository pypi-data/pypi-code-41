# coding=utf-8

""" Put a useful module description here. """
from yfmil3id2019.algorithms import addition, multiplication


def run_app(input_x, input_y, multiply, verbose):

    """ Run the application """

    if multiply:
        result = multiplication.multiply_two_numbers(input_x, input_y)

    else:
        result = addition.add_two_numbers(input_x, input_y)

    if verbose:
        if multiply:
            print("Calculating {} * {}".format(input_x, input_y))

        else:
            print("Calculating {} + {}".format(input_x, input_y))

    print("Result is {}".format(result))

    return result
