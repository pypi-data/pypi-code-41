import adapay
from adapay.api.api_request import ApiRequestor


class Bill(object):

    @classmethod
    def download(cls, **kwargs):
        url = adapay.base_url + '/v1/bill/download'
        return ApiRequestor.request(url, 'post', kwargs)


