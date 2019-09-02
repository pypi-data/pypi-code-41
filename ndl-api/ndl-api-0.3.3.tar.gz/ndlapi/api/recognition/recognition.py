"""
NeurodataLab LLC 12.04.2019
Created by Andrey Belyaev
"""
import grpc
import json
import ndlapi.api.recognition.recognition_task as CTask


class IRecognition:

    def __init__(self, auth):
        ssl_cred = grpc.ssl_channel_credentials(auth.ssl_credentials().ca(),
                                                auth.ssl_credentials().key(),
                                                auth.ssl_credentials().cert())

        token_cred = grpc.access_token_call_credentials(auth.token())

        channel_cred = grpc.composite_channel_credentials(ssl_cred, token_cred)
        self.channel = grpc.secure_channel(auth.host(), channel_cred)

        self.stub = None

    def on_image(self, image):
        result = self.stub.process_image(image.request())
        return json.loads(result.data.decode()), result.status, result.message

    def on_video(self, video):
        task_info = self.stub.process_video(video.request())
        return CTask.Task(task_info.id, self)

    def progress(self, task_info):
        return self.stub.process_progress(task_info.request())

    def result(self, task_info):
        return self.stub.process_result(task_info.request())

    def on_stream(self, stream):
        out_iterator = self.stub.process_stream(stream)
        stream.output(out_iterator)
        return stream

    @staticmethod
    def postprocess_result(result):
        return result
