import os
import time
import base64
import hmac
import hashlib

import requests


class ACRCloud:

    def __init__(self, host, access_key, access_secret):
        self.host = host
        self.access_key = access_key
        self.access_secret = access_secret

        self.endpoint = "/v1/identify"
        self.signature_version = "1"
        self.data_type = "audio"
        self.http_post_method = "POST"

    def identify(self, file_path):
        timestamp = time.time()
        string_to_sign = '\n'.join([self.http_post_method,
                                    self.endpoint,
                                    self.access_key,
                                    self.data_type,
                                    self.signature_version,
                                    str(timestamp)])

        sign = base64.b64encode(hmac.new(self.access_secret, string_to_sign.encode('utf-8'),
                                         digestmod=hashlib.sha1).digest())

        f = open(file_path, "rb")
        sample_bytes = os.path.getsize(file_path)

        files = {'sample': f}
        data = {
            'access_key': self.access_key,
            'data_type': self.data_type,
            "signature_version": self.signature_version,
            'sample_bytes': sample_bytes,
            'timestamp': str(timestamp),
            'signature': sign
        }

        url = "http://{}{}".format(self.host, self.endpoint)
        r = requests.post(url, files=files, data=data)
        return r.json()
