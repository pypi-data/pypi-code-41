"""
ap.tools

Collection of useful tooling.
"""
import ap.tools.itertools

def n_chunks(lst, k):
    return [i for i in ap.tools.itertools.n_chunks(lst, k)]

def chunk(lst, k):
    return [i for i in ap.tools.itertools.chunk(lst, k)]
