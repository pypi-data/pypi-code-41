from unary_coding import inverted_unary
from minimal_binary_coding import minimal_binary_coding


def golomb_coding(n: int, b: int) -> str:
    """Return string representing given number in golomb coding.
        n:int, number to convert to golomb.
        b:int, module.
    """
    return inverted_unary(n // b)+minimal_binary_coding(n % b, b)