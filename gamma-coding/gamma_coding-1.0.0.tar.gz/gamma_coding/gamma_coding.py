from unary_coding import inverted_unary
from reduced_binary_coding import reduced_binary_coding

def gamma_coding(n:int)->str:
    """Return string representing given number in gamma coding.
        n:int, number to convert to unary.
    """    
    rbc = reduced_binary_coding(n)
    return inverted_unary(len(rbc)) + rbc