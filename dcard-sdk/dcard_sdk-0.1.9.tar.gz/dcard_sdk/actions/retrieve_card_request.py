from dcard_sdk.base_classes import ResponseExt, HandlerExt


class Response(ResponseExt):
    def format_data(self, data):
        return super().format_data(data)['card']


class Handler(HandlerExt):
    endpoint = '/card/{public_id}'

    def __call__(self, public_id):
        url = self.get_url(public_id=public_id)
        response = self.get(url)
        return Response(response).data
