from flask import Response
import json


class CustomResponse(Response):
    def __init__(self, data, status_code=200, message="OK", **kwargs):
        response_keys = {"data", "message", "status_code"}
        response_object = {
            "data": {},
            "message": message,
            "status_code": status_code
        }
        try:
            response_object["status_code"] = int(status_code)
        except ValueError:
            raise ValueError("invalid literal for int() with base 10")
        try:
            data = json.loads(data)
            raise ValueError("Data send in json format. Please use the right format")
        except Exception as e:
            pass
        if not isinstance(message, str):
            raise ValueError("Message not in string format. Please use the right format")
        if isinstance(data, str) or isinstance(data, unicode):
            response_object["message"] = str(data)
            response_object["data"] = {}
        elif isinstance(data, list):
            response_object["message"] = message
            response_object["data"] = data
        elif isinstance(data, dict):
            if set(data.keys()).union(response_keys) == response_keys:
                if "data" in data.keys() and (isinstance(data["data"], list) or isinstance(data["data"], dict)):
                    response_object["data"] = data["data"]
                if "message" in data.keys():
                    response_object["message"] = data["message"] if isinstance(data["message"], str) else ValueError(
                        "Message not in string format. Please use the right format")
                if "status_code" in data.keys():
                    try:
                        response_object["status_code"] = int(data["status_code"])
                    except ValueError:
                        raise ValueError("invalid literal for int() with base 10")
                    status_code = response_object["status_code"]
            else:
                response_object["message"] = message
                response_object["data"] = data
        else:
            raise ValueError("Unsupported Data Structure: We only except string, dictionary and list")

        if 'content_type' not in kwargs:
            kwargs['content_type'] = "application/json"

        return super(CustomResponse, self).__init__(response=json.dumps(response_object), status=int(status_code),
                                                    **kwargs)
