import ctypes
import os

_dll_file = 'c_sum.dll'
_path = os.path.join(*(os.path.split(__file__)[:-1] + (_dll_file,)))
c_sum = ctypes.cdll.LoadLibrary(_path)  # 似乎是需要给出完整的目录