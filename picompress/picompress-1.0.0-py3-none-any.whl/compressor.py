from ctypes import *
import os
import platform

lib_version = platform.linux_distribution()
assert lib_version[0].lower() == 'ubuntu'
lib_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'so/libcompressor.so.' + lib_version[1])
ccompressor = cdll.LoadLibrary(lib_path)

ccompressor.c_compress_image.argtypes = [
    c_void_p,
    c_ulong,
    c_void_p,
    POINTER(c_ulong)
]
ccompressor.c_compress_image.restype = c_int

ccompressor.c_decompress_image.argtypes = [
    c_void_p,
    c_ulong,
    c_void_p,
    POINTER(c_ulong)
]
ccompressor.c_decompress_image.restype = c_int


class Compressor(object):

    @staticmethod
    def compress(pixels: bytes, buffer_size=50000):
        compressed_bytes = create_string_buffer(b'0', size=buffer_size)
        compressed_len = c_ulong(buffer_size)
        code = ccompressor.c_compress_image(
            pixels,
            len(pixels),
            compressed_bytes,
            byref(compressed_len)
        )
        if code != 0:
            raise ValueError('Compress Image Error! Error code:' + str(code))
        return compressed_bytes.raw[:compressed_len.value]

    @staticmethod
    def decompress(compressed: bytes, buffer_size=50000):
        decompressed_bytes = create_string_buffer(b'0', size=buffer_size)
        decompressed_len = c_ulong(buffer_size)
        code = ccompressor.c_decompress_image(
            compressed,
            len(compressed),
            decompressed_bytes,
            byref(decompressed_len)
        )
        if code != 0:
            raise ValueError('Decompress Image Error! Error code:' + str(code))
        return decompressed_bytes.raw[:decompressed_len.value]
