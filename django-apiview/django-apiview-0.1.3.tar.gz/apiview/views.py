import time
import functools
import logging
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from .annotations import Integer
from .annotations import String
from .annotations import Bytes
from .annotations import Boolean
from .utils import DjangoJsonEncoder
from .utils import request_get_dict
from .utils import get_payload
from .utils import get_inject_params


logger = logging.getLogger(__name__)

@csrf_exempt
def apiview(view):
    @functools.wraps(view)
    def wrapper(request, *args, **kwargs):
        package = {}
        try:
            data = request_get_dict(request)
            data["_request"] = request
            form = get_payload(request)
            data["_form"] = form
            for key, value in form.items():
                if not key in data:
                    data[key] = value
            if not "request" in data:
                data["request"] = request
            if not "form" in data:
                data["form"] = form
            params = get_inject_params(view, data)
            result = view(**params)
            package["success"] = True
            package["result"] = result
        except Exception as error:
            logger.exception("Error on getting result in @apiview...")
            package["success"] = False
            package["error"] = error
        return JsonResponse(package, encoder=DjangoJsonEncoder, json_dumps_params={"ensure_ascii": False})
    return wrapper


# ===========================================
# test views
# ===========================================
@apiview
def ping():
    return "pong"

@apiview
def timestamp():
    return int(time.time())

@apiview
def echo(msg):
    return msg

@apiview
def getBooleanResult(value : Boolean):
    return value

@apiview
def getIntegerResult(value: Integer):
    return value

@apiview
def getBytesResult(value: Bytes):
    return value
