"""
NeurodataLab LLC 12.04.2019
Created by Andrey Belyaev
"""
import ndlapi.api.utils.ioutil as io
import ndlapi._pyproto.api_common_pb2 as capi
import os.path as osp
from PIL import Image as pil_image


class Image:

    def __init__(self, binary, extension):
        self.binary = binary
        self.ext = extension

    @staticmethod
    def from_file(path):
        return Image(io.read_binary(path), osp.splitext(path)[1])

    @staticmethod
    def from_bgr(bgr_data):
        binary = pil_image.fromarray(bgr_data)
        return Image(binary.tobytes("jpeg"), ".jpeg")

    def request(self):
        return capi.ImageProcessingRequest(image=self.binary, extension=self.ext)
