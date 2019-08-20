import numpy as np
import pandas as pd
from multiprocessing import Pool
from functools import partial
from difflib import SequenceMatcher

def parallelize(data, func, num_of_processes=8):
    data_split = np.array_split(data, num_of_processes)
    pool = Pool(num_of_processes)
    data = pd.concat(pool.map(func, data_split))
    pool.close()
    pool.join()
    return data


def longest_common_substring(m, n):
    seqMatch = SequenceMatcher(None, m, n)
    match = seqMatch.find_longest_match(0, len(m), 0, len(n))
    return m[match.a: match.a + match.size]
