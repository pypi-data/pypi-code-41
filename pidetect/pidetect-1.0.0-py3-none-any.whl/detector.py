from ctypes import *
import os
import platform
import numpy as np

lib_version = platform.linux_distribution()
assert lib_version[0].lower() == 'ubuntu'
lib_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'so/libdetector.so.' + lib_version[1])
cdetector = cdll.LoadLibrary(lib_path)

cdetector.c_detect.argtypes = [
    c_int,
    POINTER(c_char_p),
    POINTER(c_ulong),
    POINTER(c_ulong),
    POINTER(c_ulong),
    POINTER(c_ulong),
    POINTER(c_int),
    c_char_p,
    c_char_p
]
cdetector.c_detect.restype = c_int

cdetector.c_dump.argtypes = [
    POINTER(c_void_p),
    c_ulong,
    c_ulong,
    c_ulong,
    c_ulong,
    c_byte,
    c_char_p
]
cdetector.c_dump.restype = c_int


class Detector(object):

    @staticmethod
    def detect(imgs, shapes,
               tf_server_addr=b"http://gpu-workstation:9595/",
               model_uri=b"v1/models/resnet/versions/10000000000:predict"):
        assert len(imgs) == len(shapes), "images and shapes should " \
                                         "have the same length"
        arrlen = len(imgs)
        pixel_arr = (c_char_p * arrlen)(*imgs)
        bytelen_arr = (c_ulong * arrlen)(*[len(x) for x in imgs])

        shapes = np.array(shapes)
        height_arr = (c_ulong * arrlen)(*shapes[:, 0])
        width_arr = (c_ulong * arrlen)(*shapes[:, 1])
        channel_arr = (c_ulong * arrlen)(*shapes[:, 2])
        targets = (c_int * arrlen)(*([-1] * arrlen))
        code = cdetector.c_detect(
            arrlen,
            pixel_arr,
            bytelen_arr,
            height_arr,
            width_arr,
            channel_arr,
            targets,
            tf_server_addr,
            model_uri
        )
        if code != 0:
            raise ValueError('Detect Error! Error code:' + str(code))
        results = []
        for i in range(arrlen):
            results.append(targets[i])
        return results

    @staticmethod
    def dump(pixels: bytes, shape: list or tuple, label: int, filename: str):
        filename = filename.encode('ASCII')
        code = cdetector.c_dump(
            pixels,
            len(pixels),
            shape[0],
            shape[1],
            shape[2],
            label,
            filename
        )
        if code != 0:
            raise ValueError('Dump Error! Error code:' + str(code))
