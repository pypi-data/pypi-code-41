from math import log2, ceil


def levenshtein_coding(n: int) -> str:
    """Return string representing given number in levenshtein coding.
        n:int, number to convert to levenshtein coding.
    """
    if n == 0:
        return "0"
    c, code = 1, ""
    while True:
        code = bin(n)[3:] + code
        n = ceil(log2(n+1))-1
        if n == 0:
            break
        c += 1
    return "1"*c+"0"+code


def decode_levenshtein_coding(code: str) -> int:
    """Return integer represented by given string in levenshtein coding.
        code:str, strong to decode to integer.
    """
    ones = 0
    for c in code:
        if c == "0":
            break
        ones += 1
    if ones == 0:
        return 0
    n = 1
    offset = ones+1
    for _ in range(ones-1):
        new_n = int("1"+code[offset:offset+n], 2)
        offset += n
        n = new_n

    return n