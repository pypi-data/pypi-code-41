"""
ap.itertools

A collection of iterator-based tools
"""

def _index(i, n, k):
    return i * (n // k) + min(i, n % k)

def n_chunks(lst, k):
    """Split list into pieces of approximately k-size"""
    n = len(lst)
    for i in range(k):
        yield lst[_index(i, n, k):_index(i + 1, n, k)]

def chunk(lst, k):
    """Split list into k approximately even lists"""
    for i in range(0, len(lst), k):
        yield lst[i:i + k]
