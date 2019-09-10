def reduced_binary_coding(n: int) -> str:
    """Return string representation reduced binary coding for given integer.
        n:int, integer to be converted.
    """
    return bin(n+1)[3:]
