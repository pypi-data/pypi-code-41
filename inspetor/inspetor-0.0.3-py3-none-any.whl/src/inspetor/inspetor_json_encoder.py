import json
from json import JSONDecoder

from src.inspetor.model.inspetor_abstract_model import InspetorAbstractModel

class AbstractModelEncoder(JSONDecoder):
    def default(self, object):
        if isinstance(object, InspetorAbstractModel):
            return object.__dict__
        return json.JSONDecoder.default(self, object)