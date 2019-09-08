from math import floor, log2

def truncated_binary_encoding(n: int, b: int) -> str:
    """Return string representing given number in truncated binary encoding.
        n:int, number to convert to truncated binary encoding.
        b:int, maximal size.
    """
    k = floor(log2(b))
    u = (1 << k+1) - b
    return f"{{0:0{k}b}}".format(n if n < u else n+u)