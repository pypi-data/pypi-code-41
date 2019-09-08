# -*- coding:utf-8 -*-
"""
Hello from Tools/Math/Arrange.py

Classes:
    Arrange(int)
        __new__
            Create a Arrange object.
Functions:
    ArrangeMethods
        This function allows you to easily get all the methods of arrange.
    Demo
        This function is a demo of all functions and classes in this module.
"""

from itertools import permutations as p


class Arrange(int):
    """
    This is the arrangement in mathematics.

    The arrangement in mathematics looks like this:
                m
              A
                n
    This is how many permutation methods are used
    to extract m elements from n elements.
    For example:
                2
              A    == 5 * 4 == 20
                5
    - - - - - - - - - - - - - - - - - - - - - -
                5
              A    == 7 * 6 * 5 * 4 * 3 == 2520
                7
    - - - - - - - - - - - - - - - - - - - - - -
                3
              A    == 10 * 9 * 8 == 720
                10
    This class allows you to easily calculate the number of methods arranged.
    """
    def __new__(cls, n, m):
        """
        Create a Arrange object.

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
        num = 1
        for i in range(m):
            num *= n - i
        return int.__new__(cls, num)


def ArrangeMethods(nums, elements_number):
    """
    This function allows you to easily get all the methods of arrange.

    Parameters
    ----------
    nums: list
        They are all the elements that need to be arranged.
    elements_number: int
        It is the number of elements to be taken out.

    Returns
    -------
    tuple
        This tuple have two elements,
        the first is all the permutation methods (list),
        the second is the Arrange object (Arrange(len(nums, elements_number))).
    """
    return (list(p(nums, elements_number)),
            Arrange(len(nums), elements_number))


def Demo():
    """This function is a demo of all functions and classes in this module."""
    print(Arrange(9, 2))    # == 9 * 8
    print(Arrange(8, 4))    # == 8 * 7 * 6 * 5
    print(ArrangeMethods([i for i in range(1, 11)], 3))
    print(ArrangeMethods([i for i in range(12)], 4))


if __name__ == '__main__':
    Demo()
