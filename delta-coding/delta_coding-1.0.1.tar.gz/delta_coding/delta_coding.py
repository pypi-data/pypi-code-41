from gamma_coding import gamma_coding
from reduced_binary_coding import reduced_binary_coding


def delta_coding(n: int) -> str:
    """Return string representing given number in delta coding.
        n:int, number to convert to unary.
    """
    rbc = reduced_binary_coding(n)
    return gamma_coding(len(rbc)) + rbc
