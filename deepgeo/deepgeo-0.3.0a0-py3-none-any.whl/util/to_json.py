import numpy as np

def default_DICT_TO_JSON(o):
    if isinstance(o, np.int8): return int(o)  
    if isinstance(o, np.int16): return int(o)  
    if isinstance(o, np.int32): return int(o)  
    if isinstance(o, np.int64): return int(o)  