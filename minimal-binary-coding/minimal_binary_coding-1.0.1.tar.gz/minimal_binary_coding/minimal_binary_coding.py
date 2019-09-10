from math import log2, ceil


def minimal_binary_coding(n: int, b: int) -> str:
    """Return string representing given number in minimal binary coding.
        n:int, number to convert to minimal binary encoding.
        b:int, maximal size.
    """
    if n == 0 and b == 1:
        return ""
    s = ceil(log2(b))
    if n < 2**s - b:
        return f"{{0:0{s-1}b}}".format(n)
    return f"{{0:0{s}b}}".format(n-b+2**s)
