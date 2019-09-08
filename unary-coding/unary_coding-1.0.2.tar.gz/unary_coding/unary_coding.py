def _unary(n:int, zero:str, one:str)->str:
    return one*n + zero

def unary(n:int)->str:
    """Return string representing given number in unary.
        n:int, number to convert to unary.
    """
    return _unary(n, "0", "1")

def inverted_unary(n:int)->str:
    """Return string representing given number in inverted unary.
        n:int, number to convert to unary.
    """
    return _unary(n, "1", "0")