# -*- coding:utf-8 -*-
"""
Hello from Tools/Math/Combination.py

Classes:
    Combination(int)
        __new__
            Create a Combination object.
Functions:
    CombinationMethods
        This function allows you to easily get all the methods of combination.
    Demo
    This function is a demo of all functions and classes in this module.
"""

from Arrange import Arrange as Ar
from itertools import combinations as c


class Combination(int):
    """
    This is the combination in mathematics.

    The combination in mathematics looks like this:
                m
              C
                n
    This is a combination method of extracting m elements
    from n elements (without considering the order).
    For example:
                2       2       2
              C    == A    /  A    == (5 * 4) / (2 * 1) == 20 / 2 == 10
                5       5       2
    - - - - - - - - - - - - - - - - - - - - - -
                5       5       5
              C    == A    /  A    == (7 * 6 * 5 * 4 * 3) / (5 * 4 * 3 * 2 * 1) == 2520 / 120 == 21
                7       7       5
    - - - - - - - - - - - - - - - - - - - - - -
                3       3       3
              C    == A    /  A    == (10 * 9 * 8) / (3 * 2 * 1) == 720 / 6 == 120
                10      10      3
    This class allows you to easily calculate the number of combination methods.
    """
    def __new__(cls, n, m):
        """
        Create a Combination object.

        Parameters
        ----------
        n: int
            A number, please see above.
        m: int
            A number, please see above.

        Returns
        -------
        Arrange
            Return its case.
        """
        assert n >= m
        assert m > 0
        assert n > 0
        assert isinstance(n, int) and isinstance(m, int)
        return int.__new__(cls, Ar(n, m) / Ar(m, m))


def CombinationMethods(nums, elements_number):
    """
    This function allows you to easily get all the methods of combination.

    Parameters
    ----------
    nums: list
        They are all the elements that need to be combined.
    elements_number: int
        It is the number of elements to be taken out.

    Returns
    -------
    tuple
        This tuple have two elements,
        the first is all the combination methods (list),
        the second is the Combination object (Combination(len(nums, elements_number))).
    """
    res = list(c(nums, elements_number))
    return res, Combination(len(nums), elements_number)


def Demo():
    """This function is a demo of all functions and classes in this module."""
    print(Combination(8, 4))
    print(CombinationMethods([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 3))


if __name__ == '__main__':
    Demo()
