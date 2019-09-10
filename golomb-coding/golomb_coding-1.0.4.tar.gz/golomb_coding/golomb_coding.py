from unary_coding import inverted_unary
from minimal_binary_coding import minimal_binary_coding
from typing import List
from math import log2, ceil


def golomb_coding(n: int, b: int) -> str:
    """Return string representing given number in golomb coding.
        n:int, number to convert to golomb coding.
        b:int, module.
    """
    return inverted_unary(n // b)+minimal_binary_coding(n % b, b)


def optimal_golomb_coding(n: int, p: float) -> str:
    """Return string representing given number in optimal golomb coding.
        n:int, number to convert to optimal golomb coding.
        p:float, probability for given number n.
    """
    return golomb_coding(n, ceil(-1 / log2(1-p)))


def bernoulli_golomb_coding(numbers: List[int]) -> List[str]:
    """Return list of strings representing given numbers in bernoulli golomb coding.
        numbers: List[int], list of numbers to convert to bernoulli golomb coding.
    """
    frequencies = {}
    N = len(numbers)
    for n in numbers:
        frequencies[n] = frequencies.get(n, 0) + 1

    return [
        optimal_golomb_coding(n, frequencies[n]/N) for n in numbers
    ]
