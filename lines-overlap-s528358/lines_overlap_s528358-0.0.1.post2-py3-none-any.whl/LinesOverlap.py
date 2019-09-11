def checkLinesOverlap(line1=None, line2=None):
    
    if line1 is None and line2 is None:
        raise ValueError("checkLinesOverlap() needs two arguments (0 given)")
    elif line1 is None or line2 is None:
        raise ValueError("checkLinesOverlap() needs two arguments (1 given)")
    elif not isinstance(line1, tuple) or not isinstance(line2, tuple):
        raise ValueError("both arguments must be of type tuple")
    elif not isinstance(line1[0], int) or not isinstance(line1[1], int) or not isinstance(line2[0], int) or not isinstance(line2[1], int):
        raise ValueError("lines must be of type int, not str")  
    
    return Solution(line1[0], line1[1], line2[0], line2[1]) or Solution(line2[0], line2[1], line1[0], line1[1])

def Solution(a, b, c, d):
    return min(c,d)<=a<=max(c,d) or min(c,d)<=b<=max(c,d)