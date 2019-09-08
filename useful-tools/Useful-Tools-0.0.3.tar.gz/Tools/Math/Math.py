# -*- coding:utf-8 -*-

"""
Hello from Tools/Math/Math.py

Functions:
    GCD
        Return the greatest common divisor of integers.
    MCM
        Return the minimum common multiply of integers.
    Modef
        Return the fractional and integer parts of x.
    Demo
        This function is a demo of all functions and classes in this module.
"""

# import
import math as __math


# functions
def GCD(*nums):
    """
    Return the greatest common divisor of integers.

    Parameters
    ----------
    nums: integers
        Many integers.

    Returns
    -------
    int
        It's the greatest common divisor of integers.
    """
    assert nums

    gcdl = []
    for i in range(1, sorted(nums)[0] + 1):
        for index, j in enumerate(nums):
            if j % i == 0:
                if (index + 1) == len(nums):
                    gcdl.append(i)
                    break
                continue
            else:
                break
    if not gcdl:
        return 1
    else:
        return list(sorted(gcdl))[-1]


def MCM(*nums):
    """
    Return the minimum common multiply of integers.

    Parameters
    ----------
    nums : integers
        They must be integers, not zero.

    Returns
    -------
    int
        It's the minimum common multiply of integers.
    """
    minimum = 1
    for i in nums:
        minimum = int(i) * int(minimum) / __math.gcd(int(i), int(minimum))
    return int(minimum)


def Modef(x):
    """
    Return the fractional and integer parts of x.
    Both results carry the sign of x and are floats.

    Parameters
    ----------
    x : int or float
        A number.

    Returns
    -------
    tuple
        The first element is the fractional part of x,
        and the second element is the integer part of x.
    """
    dot = str(x).find('.')
    digit = len(str(x)[dot + 1:len(str(x))])
    a = float(int(x))
    b = x - a
    b = round(b, digit)
    return b, a


def Demo():
    """This function is a demo of all functions and classes in this module."""
    print(GCD(8, 6, 140))
    print(MCM(1, 2, 3, 4, 5))
    print(Modef(2.5))


if __name__ == '__main__':
    Demo()
