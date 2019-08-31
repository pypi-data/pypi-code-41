import inspect
import json
import binascii
import bizerror
from django.db import models
from django.core.serializers.json import DjangoJSONEncoder as DjangoJSONEncoderBase
from django.forms.models import model_to_dict
from django.core import serializers

def model_to_json(o):
    text = serializers.serialize("json", [o])
    results = json.loads(text)
    obj = results[0]["fields"]
    obj["pk"] = results[0]["pk"]
    return obj

def queryset_to_json(q):
    text = serializers.serialize("json", q)
    results = json.loads(text)
    data = []
    for result in results:
        obj = result["fields"]
        obj["pk"] = result["pk"]
        data.append(obj)
    return data

class DjangoJsonEncoder(DjangoJSONEncoderBase):

    def default(self, o):
        if isinstance(o, bytes):
            return binascii.hexlify(o).decode()
        if isinstance(o, models.Model):
            return model_to_json(o)
        if isinstance(o, models.QuerySet):
            return queryset_to_json(o)
        if isinstance(o, bizerror.BizError):
            return o.json
        if isinstance(o, Exception):
            return bizerror.UndefinedError(str(o)).json
        return super().default(o)

def request_get_dict(request):
    data = {}
    for name, _ in request.GET.items():
        value = request.GET.getlist(name)
        if isinstance(value, (list, tuple, set)) and len(value) == 1:
            data[name] = value[0]
        else:
            data[name] = value
    return data

def get_payload(request):
    if request.body:
        try:
            return json.loads(request.body)
        except:
            pass
    return {}

def get_inject_params(func, data):
    params = {}
    parameters = inspect.signature(func).parameters
    for name, parameter in parameters.items():
        if parameter.default is parameter.empty: # 没有默认值，为必选参数
            value = data[name]
        else:
            value = data.get(name, parameter.default)
        if not parameter.annotation is parameter.empty:
            value = parameter.annotation(value)
        params[name] = value
    return params
