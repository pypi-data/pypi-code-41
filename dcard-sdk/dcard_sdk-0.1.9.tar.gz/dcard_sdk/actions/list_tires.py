from dcard_sdk.base_classes import ResponseExt, HandlerExt


class Response(ResponseExt):
    def format_data(self, data):
        return super().format_data(data)['tires']


class Handler(HandlerExt):
    endpoint = '/tires'

    def __call__(self):
        url = self.get_url()
        response = self.get(url)
        return Response(response).data
