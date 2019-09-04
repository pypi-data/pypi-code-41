"""
2019.8.1 create by yumin.chang
调用支付接口
"""

import adapay

from adapay.api.api_request import ApiRequestor


class Charge(object):

    @classmethod
    def create(cls, **kwargs):
        """
        创建订单
        """
        return ApiRequestor.request(adapay.base_url + '/v1/charges', 'post', kwargs)

    @classmethod
    def query(cls, charge_id):
        """
        支付查询
        """
        url = (adapay.base_url + '/v1/charges/{charge_id}').format(charge_id=charge_id)
        return ApiRequestor.request(url, 'get', {'charge_id': charge_id})

    @classmethod
    def close(cls, **kwargs):
        """
        关单请求
        """
        url = (adapay.base_url + '/v1/charges/{}/close').format(kwargs['charge_id'])
        return ApiRequestor.request(url, 'post', kwargs)

