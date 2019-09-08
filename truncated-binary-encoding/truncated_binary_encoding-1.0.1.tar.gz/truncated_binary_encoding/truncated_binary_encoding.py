from math import ceil, log2

def truncated_binary_encoding(n: int, b: int) -> str:
    """Return string representing given number in truncated binary encoding.
        n:int, number to convert to truncated binary encoding.
        b:int, maximal size.
    """
    return f"{{0:0{ceil(log2(b))}b}}".format(n)