import math


def get_digit_zero_based(index: int) -> int:
    """
    Finds digit that is placed on 0-based index in string of numbers from zero to infinity.

    :param int index: index
    :return: digit on index in string from zero to infinity
    :rtype: int
    """
    digits_amount = 1
    bound = 9
    number = 0
    while index > bound:
        number += bound
        index -= bound
        bound *= 10
        digits_amount += 1
    offset = math.ceil(index / digits_amount)
    number += offset
    return int(str(number)[digits_amount - 1 - (digits_amount * offset - index)])


def get_digit_one_based(index: int) -> int:
    """
    Finds digit that is placed on 0-based index in string of numbers from one to infinity.

    :param int index: index
    :return: digit on index in string from one to infinity
    :rtype: int
    """
    return get_digit_zero_based(index + 1)
