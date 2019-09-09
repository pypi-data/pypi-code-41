from math import ceil, log2


def _nibble_coding(n: int, b: int) -> str:
    """Return string representing given number in b-nibble coding.
        n:int, number to convert to nibble coding.
        b:int, chunk size.
    """
    k, r = 1, 1 << b
    if n != 0:
        k = ceil(log2(n+1)/b)    
        r += sum([
            (n & (((1 << b)-1) << (b*i))) << i for i in range(k)
        ])
    return f"{{0:0{k*(b+1)}b}}".format(r)


def nibble_coding(n: int) -> str:
    """Return string representing given number in nibble coding.
        n:int, number to convert to nibble coding.
    """
    return _nibble_coding(n, 3)


def byte_coding(n: int) -> str:
    """Return string representing given number in byte coding.
        n:int, number to convert to byte coding.
    """
    return _nibble_coding(n, 7)
