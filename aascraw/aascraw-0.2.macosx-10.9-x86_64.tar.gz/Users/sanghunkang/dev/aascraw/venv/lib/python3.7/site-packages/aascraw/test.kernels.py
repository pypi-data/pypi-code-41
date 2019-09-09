# Test module for kernel functions
import numpy as np

from functools import reduce
import ctypes

c_kernels = ctypes.CDLL("./kernels.so")

# Test Inputs
xpath_set = [
    "Some",
    "arbitasdasdrary",
    "length",
    "string",
    "string",
    "string"
]



# rank_tuple_vicinity
SIZE_XPATH_SET = len(xpath_set)
c_kernels.rank_tuple_vicinity.restype = ctypes.c_float #ctypes.c_int

def rank_tuple_vicinity(xpath_set, existing_records):
    xpath_set = [bytes(xpath, "utf-8") for xpath in xpath_set]
    xpath_set.append(None)
    # s.encode('utf-8') or bytes(s, 'utf-8')
    c_kernels.rank_tuple_vicinity.argtypes = (ctypes.c_wchar_p * (SIZE_XPATH_SET+1), )

    arr = (ctypes.c_wchar_p * (SIZE_XPATH_SET+1))(*xpath_set)
    # arr = xpath_set
    # parameter_array = arr(*xpath_set)
    # return c_kernels.rank_tuple_vicinity(parameter_array)
    return c_kernels.rank_tuple_vicinity(arr)

print(SIZE_XPATH_SET)
aa = rank_tuple_vicinity(xpath_set, None)
print(aa)