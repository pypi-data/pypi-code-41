from math import log2, ceil


def omega_coding(n: int) -> str:
    """Return string representing given number in omega coding.
        n:int, number to convert to omega coding.
    """
    code = "0"
    while n > 1:
        code = bin(n)[2:] + code
        n = ceil(log2(n+1))-1
    return code


def decode_omega_coding(code: str) -> int:
    """Return integer represented by given string in omega coding.
        code:str, strong to decode to integer.
    """
    n, c = 1, 0
    while code[c] != "0":
        new_n = int(code[c:c+1+n], 2)
        c += n + 1
        n = new_n
    return n
