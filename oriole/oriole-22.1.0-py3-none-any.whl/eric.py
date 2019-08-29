#!/usr/bin/env python

import ctypes
from os.path import dirname, join


class Eric:
    def __init__(self, mod=join(dirname(__file__), 'alg.so')):
        lib = ctypes.cdll.LoadLibrary(mod)
        self.encode = lib.Encode
        self.encode.argtypes = [ctypes.c_char_p]
        self.encode.restype = ctypes.POINTER(ctypes.c_ubyte * 8)
        self.decode = lib.Decode
        self.decode.argtypes = [ctypes.c_char_p]
        self.decode.restype = ctypes.POINTER(ctypes.c_ubyte * 8)

    def enc(self, bytes_data):
        ptr = self.encode(bytes_data)
        length = int.from_bytes(ptr.contents, "little")
        data = bytes(
            ctypes.cast(ptr, ctypes.POINTER(ctypes.c_ubyte *
                                            (8 + length))).contents[8:])
        return data

    def dec(self, bytes_data):
        ptr = self.decode(bytes_data)
        length = int.from_bytes(ptr.contents, "little")
        data = bytes(
            ctypes.cast(ptr, ctypes.POINTER(ctypes.c_ubyte *
                                            (8 + length))).contents[8:])
        return data
