import requests
import cv2
import base64
import json, time
import numpy as np
from .server import BaseHandler

requests.adapters.DEFAULT_RETRIES = 5


class ImageServer:
    def __init__(self, server_address):
        self.session = requests.session()

        self.server_address = server_address

    @staticmethod
    def encode_warpimg(image, input={}):
        """
        input image to server need to encode base64
        """
        if isinstance(image, bytes):
            enbuf = base64.b64encode(image).decode('utf-8')
        elif isinstance(image, np.ndarray):
            enbuf = base64.b64encode(cv2.imencode('.jpg', image)[1].tostring()).decode('utf-8')
        else:
            enbuf = 'null'

        input['image_type'] = 'base64'
        input['image_base64'] = enbuf
        return input

    def send(self, indict, times=3):
        param = json.dumps(indict)

        resp_dict = BaseHandler.build_resp((False, "connect failed"))
        while times > 0:
            try:
                req = self.session.post(self.server_address, headers={"Content-Type": 'application/json'}, data=param)

                if isinstance(req.text, str):
                    resp_dict = json.loads(req.text)
                else:
                    resp_dict = json.loads(req.text.encode('unicode-escape').decode('string_escape'))
                break
            except requests.exceptions.ConnectionError:
                time.sleep(1)

            times -= 1

        return resp_dict


if __name__ == '__main__':
    server = ImageServer('http://0.0.0.0:8080/inference')
    image = cv2.imread('1.png', cv2.IMREAD_COLOR)
    idict = ImageServer.encode_warpimg(image)
    ret = server.send(idict)
    print(ret)
