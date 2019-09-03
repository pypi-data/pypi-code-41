from dcard_sdk.base_classes import ResponseExt, HandlerExt


class Response(ResponseExt):
    pass


class Handler(HandlerExt):
    endpoint = '/card/print/{card_id}/{template_id}'

    def __call__(self, public_id):
        url = self.get_url(card_id=public_id, template_id=self.config['TEMPLATE_ID'])
        response = self.get(url)
        return Response(response).data
