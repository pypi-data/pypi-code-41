from minimal_binary_coding import minimal_binary_coding
from typing import List


def interpolative_coding(numbers: List[int], low: int, high: int) -> str:
    """Return list with interpolative coding of given numbers
        numbers:List[int], list of integers to be converted to interpolative coding.
        low:int, lowest value known.
        high:int, highest value known.
    """
    if len(numbers) == 0:
        return [""]
    if len(numbers) == 1:
        return [minimal_binary_coding(numbers[0]-low, high)]
    h = (len(numbers) + 1) // 2
    n = numbers[h-1]
    return interpolative_coding(numbers[:h-1], low, n) + [
        minimal_binary_coding(n-(low + h - 1), high - (len(numbers) - h)),
    ] + interpolative_coding(numbers[h+1:], n+1, high)
