from enum import Enum
import requests
from .model import *

API_VERSION = "0.1"
TIMEOUT = 30000
SUCCESS_CODE = 200


class Language(Enum):
    EN = "en"
    ZH = "zh"


class AtmanParser(object):
    def __init__(self, endpoint, language):

        self.endpoint = endpoint
        self.language = language

        if self.language == Language.EN:
            self.language = "en"
        else:
            self.language = "zh"

    def parse(self, text):
        """Post text to the Preprocess Server

        :param (str|OrderedDict) text : raw text for the server to parse
        :return: preprocessed text
        """
        content = {
            "apiVersion": API_VERSION,
            "data": {
                "text": str(text),
                "language": self.language
            }
        }

        r = requests.post(url=self.endpoint, json=content, timeout=TIMEOUT)
        if r.status_code == SUCCESS_CODE:
            r = json.loads(r.text)
            result = Document(jstr=r['data']['preprocessedText'])
            return result

        return r.text
