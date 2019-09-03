from dcard_sdk.base_classes import ResponseExt, HandlerExt


class Response(ResponseExt):
    pass


class Handler(HandlerExt):
    endpoint = '/card/deny/{public_id}'

    def __call__(self, public_id):
        url = self.get_url(public_id=public_id)
        response = self.post(url)
        return Response(response).data
