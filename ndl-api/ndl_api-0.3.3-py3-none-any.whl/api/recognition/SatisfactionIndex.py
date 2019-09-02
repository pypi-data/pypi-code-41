"""
NeurodataLab LLC 22.08.2019
Created by Andrey Belyaev
"""
import ndlapi.api.recognition.recognition as RC
import ndlapi._pyproto.SatisfactionIndexService_pb2_grpc as si_pb2_grpc
from ndlapi.api.recognition.EmotionRecognition import SingleFrameEmotionRecognition


class SatisfactionIndexDetector(RC.IRecognition):
    short_name = 'si'

    def __init__(self, auth):
        super().__init__(auth)
        self.stub = si_pb2_grpc.SatisfactionIndexStub(self.channel)

    @staticmethod
    def postprocess_result(result):
        fd_er_result = SingleFrameEmotionRecognition.postprocess_result(result)
        for key, val in result['SatisfactionIndex'].items():
                for i, v in enumerate(val):
                    try:
                        fd_er_result[key][i]['satisfaction_index'] = v
                    except:
                        pass
        return fd_er_result
