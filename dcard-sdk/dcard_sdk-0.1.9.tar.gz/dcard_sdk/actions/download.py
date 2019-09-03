from dcard_sdk.base_classes import HandlerExt, Response as BaseResponse
from io import BytesIO


class Response(BaseResponse):
    def __init__(self, response):
        content = response.content
        self._data = BytesIO(content)


class Handler(HandlerExt):
    def __call__(self, url):
        response = self.get(url)
        return Response(response).data
