# -*- coding: utf-8 -*

from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User

from requests.structures import CaseInsensitiveDict

from kwikapi import BaseRequest, BaseResponse
from kwikapi import BaseRequestHandler, BaseAuthAPI
from kwikapi import BearerServerAuthenticator
from kwikapi import BasicServerAuthenticator


class BasicAuthenticator(BasicServerAuthenticator):
    USER_ATTRS = ("id", "email", "first_name", "last_name")

    def authenticate(self, request):
        auth = super().authenticate(request)
        username = auth.username.decode("utf8")
        password = auth.password.decode("utf8")

        user = authenticate(
            request=request.raw_request, username=username, password=password
        )

        if not user:
            return auth

        auth.is_authenticated = True
        auth.update({a: getattr(user, a) for a in self.USER_ATTRS})
        return auth


class SessionAuthenticator(BearerServerAuthenticator):
    # FIXME: this needs to be completed

    def authenticate(self, request):
        auth = super().authenticate(request)
        session_id = auth.token


class DjangoRequest(BaseRequest):
    def __init__(self, request):
        super().__init__()
        self.raw_request = self._request = request
        self._headers = self._load_headers()
        self.response = DjangoResponse(self._request)

    def _load_headers(self):
        hdrs = CaseInsensitiveDict()

        for k, v in self._request.META.items():
            if not k.startswith("HTTP_"):
                continue

            k = "-".join(k.split("_")[1:])
            hdrs[k] = v

        return hdrs

    @property
    def url(self):
        return self._request.get_full_path()

    @property
    def method(self):
        return self._request.method

    @property
    def body(self):
        return self._request.body

    @property
    def headers(self):
        return self._headers


class DjangoResponse(BaseResponse):
    def __init__(self, request):
        self._request = request
        self.raw_response = self._response = None
        self._headers = {}

    def write(self, data, proto, stream=False):
        n, t = super().write(data, proto, stream=stream)

        data = self._data
        r = StreamingHttpResponse(data) if stream else HttpResponse(data)

        for k, v in self._headers.items():
            r[k] = v

        self.raw_response = self._response = r

        return n, t

    def flush(self):
        self._response.flush()

    def close(self):
        # Django response doesn't support a close method
        # so we do nothing here.
        pass

    @property
    def headers(self):
        return self._headers


class RequestHandler(BaseRequestHandler):
    PROTOCOL = BaseRequestHandler.DEFAULT_PROTOCOL

    def handle_request(self, request):
        fn = lambda: super(RequestHandler, self).handle_request(DjangoRequest(request))

        if self.api.threadpool:
            f = self.api.threadpool.submit(fn)
            return f.result()
        else:
            return fn()
