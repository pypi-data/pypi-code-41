import base64
import string
from datetime import datetime
from src.inspetor.exception.model_exception.inspetor_general_exception import InspetorGeneralException


class InspetorAbstractModel(object):

    def encode_array(self, array, isObject):
        encoded_array = []
        if array is None:
            return None
        for item in array:
            if isObject is True:
                encoded_array.append(self.encodeObject(item))
            else:
                encoded_array.append(self.encode_data(item))
        return encoded_array

    def encode_data(self, data):
        if data is not None:
            # We have to make data an string so we can incode a bool
            data = str(base64.b64encode(str(data).encode("utf-8")), "utf-8")

        return data

    def encodeObject(self, object):
        if object is not None:
            return object.jsonSerialize()

        return object

    def inspetor_date_formatter(self, timestamp):
        if timestamp is None:
            return None

        if not isinstance(int(timestamp), int):
            raise InspetorGeneralException(
                InspetorGeneralException.WRONG_TIMESTAMP_TYPE
            )

        return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S+0000')

    # You can find this code here: https://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string
    def remove_punctuation(self, data):
        if data is not None:
            data_as_string = str(data)
            data_without_punctuation = data_as_string.translate(str.maketrans("", "", string.punctuation))
            return data_without_punctuation.replace(" ", "")
        
        return None