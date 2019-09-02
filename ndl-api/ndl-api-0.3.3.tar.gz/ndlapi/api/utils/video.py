"""
NeurodataLab LLC 12.04.2019
Created by Andrey Belyaev
"""
import ndlapi._pyproto.api_common_pb2 as capi
import os.path as osp


class Video:

    def __init__(self, stream, extension):
        self.stream = stream
        self.extension = extension
        self.BATCH = 1024 ** 2 * 3 #100 Mb

    @staticmethod
    def from_file(path):
        file_stream = open(path, "rb")
        return Video(file_stream, osp.splitext(path)[1])

    def request(self):
        while True:
            batch = self.stream.read(self.BATCH)

            if len(batch) == 0:
                return

            yield capi.VideoProcessingRequest(video_data=batch, extension=self.extension)