from unary_coding import inverted_unary
from truncated_binary_encoding import truncated_binary_encoding


def golomb_coding(n: int, b: int) -> str:
    """Return string representing given number in golomb coding.
        n:int, number to convert to golomb.
        b:int, module.
    """
    return inverted_unary(n // b)+truncated_binary_encoding(n % b, b)