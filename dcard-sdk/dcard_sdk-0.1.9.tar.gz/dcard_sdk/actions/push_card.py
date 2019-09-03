from schema import Schema, Optional

from dcard_sdk.base_classes import ResponseExt, HandlerExt


class Response(ResponseExt):
    pass


class Handler(HandlerExt):
    endpoint = '/card/push/{public_id}'
    schema = Schema({
        Optional('city_id'): int
    })

    def __call__(self, public_id, data):
        url = self.get_url(public_id=public_id)
        payload = self.schema.validate(data)
        response = self.post(url, payload)
        return Response(response).data
