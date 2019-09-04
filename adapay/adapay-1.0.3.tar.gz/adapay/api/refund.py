"""
2019.8.1 create by jun.hu
退款接口
"""

import adapay
from adapay.api.api_request import ApiRequestor


class Refund(object):

    @classmethod
    def create(cls, **kwargs):
        """
        发起退款流程
        """

        url = (adapay.base_url + '/v1/charges/{charge_id}/refunds').format(charge_id=kwargs.get('charge_id', ''))
        return ApiRequestor.request(url, 'post', kwargs)

    @classmethod
    def query(cls, **kwargs):
        """
        退款流程查询
        """

        return ApiRequestor.request(adapay.base_url + '/v1/charges/refunds', 'get', kwargs)

