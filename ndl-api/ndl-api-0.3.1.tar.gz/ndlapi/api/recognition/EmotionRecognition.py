"""
NeurodataLab LLC 12.04.2019
Created by Andrey Belyaev
"""
import ndlapi.api.recognition.recognition as RC
import ndlapi._pyproto.MultiFrameEmotionService_pb2_grpc as mf_pb2_grpc
import ndlapi._pyproto.SingleFrameEmotionService_pb2_grpc as sf_pb2_grpc


class SingleFrameEmotionRecognition(RC.IRecognition):
    short_name = 'sf_er'

    def __init__(self, auth):
        super().__init__(auth)
        self.stub = sf_pb2_grpc.SingleFrameEmotionStub(self.channel)

    @staticmethod
    def postprocess_result(result):
        fd_result = result['FaceDetector']['cutted_result']
        er_result = result['SingleFrameEmotionsDetector']

        er_result_balanced = {}
        blob_size = len(er_result[sorted(er_result.keys())[0]])
        for blob_num, blob_info in er_result.items():
            for im_num, faces_info in enumerate(blob_info):
                er_result_balanced[str(int(blob_num) * blob_size + im_num)] = faces_info

        for key in fd_result.keys():
            for n in range(len(fd_result[key])):
                fd_result[key][n]['emotions'] = er_result_balanced[key][n]

        return fd_result


class MultiFrameEmotionDetector(RC.IRecognition):
    short_name = 'mm_er'

    def __init__(self, auth):
        super().__init__(auth)
        self.stub = mf_pb2_grpc.MultiFrameEmotionStub(self.channel)

    @staticmethod
    def postprocess_result(result):
        fd_result = result['FaceDetector']['cutted_result']
        fc_result = result['FaceClustering']['result']['FaceDetector']
        mm_result = result['MultiFrameEmotionsDetector']['person_stats']

        total_result = {}
        for image_num, faces in fd_result.items():
            image_result = []
            for face, face_id in zip(faces, fc_result[image_num]):
                face['id'] = face_id
                face['emotions'] = {}
                if face_id in mm_result or str(face_id) in mm_result:
                    if str(face_id) in mm_result:
                        face_id = str(face_id)
                    if image_num in mm_result[face_id]:
                        face['emotions'] = mm_result[face_id][image_num]
                image_result.append(face)
            total_result[image_num] = image_result

        return total_result

    def on_stream(self, stream):
        raise Exception("on_stream() method is not supported for MultiFrameEmotionDetector.")

    def on_image(self, image):
        raise Exception("on_image() method is not supported for MultiFrameEmotionDetector")
