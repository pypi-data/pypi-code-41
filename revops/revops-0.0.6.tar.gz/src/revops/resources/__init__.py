from datetime import datetime, timezone
from urllib.error import HTTPError

import json


class APIResource(object):
    _api = None
    _data = ''
    _resource = None
    _marshaler = None
    _errors = None

    def __init__(self, api, **kwargs):
        self._api = api

        for key, value in kwargs.items():
            setattr(self, key, value)

    def _update_request(self):
        marshal = self._marshaler()
        self._data, self._errors = marshal.dumps(self)

    def _copy_properties(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def request(self,
        data = None,
        api = None,
        sub_resource = "",
        http_method = "GET",
        debug = False,
        ):
        if api != None:
            self._api = api
        if data != None:
            self._data = data

        if self._resource == None:
            raise Exception("Unable to send request, no _resource defined for {}".format(self))

        self._update_request()
        response = self._api.request(
            http_method = http_method,
            data = self._data,
            api_resource = "{}{}".format(self._resource, sub_resource),
        )

        if response.status_code == 400:
            raise HTTPError(
                code=response.status_code,
                url=response.url,
                fp=None,
                msg=response.content,
                hdrs=response.headers
            )

        if response.status_code == 204:
            return None

        parsed = json.loads(response.content)

        if debug == True:
            print(json.dumps(parsed, indent=4, sort_keys=True))
            
        klass = type(self)
        return klass(api=self._api, **parsed)

    def get_current_time(self):
        return datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
