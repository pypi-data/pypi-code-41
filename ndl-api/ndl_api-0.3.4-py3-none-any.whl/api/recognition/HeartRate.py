import json
import ndlapi.api.recognition.recognition as RC
import ndlapi._pyproto.HeartRateService_pb2_grpc as hrd_pb2_grpc


class HearRateDetector(RC.IRecognition):
    short_name = 'hr'

    def __init__(self, auth):
        super().__init__(auth)
        self.stub = hrd_pb2_grpc.HeartRateDetectorStub(self.channel)

    def on_image(self, image):
        raise Exception("Not supported")

    def on_stream(self, stream):
        raise Exception("Not supported")

    @staticmethod
    def postprocess_result(result):
        fd_result = result['FaceDetector']['cutted_result']
        hr_result = result['HeartRate']['cutted_result']

        total_result = {}
        for image_key, faces in fd_result.items():
            if len(faces) == 0:
                result[image_key] = []
            else:
                big_face = sorted(faces, key=lambda f: float(f['w']) * float(f['h']))[-1]
                big_face['hr'] = hr_result[image_key] if image_key in hr_result else None
                total_result[image_key] = [big_face]

        return total_result
