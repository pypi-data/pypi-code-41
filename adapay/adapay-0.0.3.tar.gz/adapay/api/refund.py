"""
2019.8.1 create by jun.hu
退款接口
"""

import adapay
from adapay.adapay_obj import AdapayObject
from adapay.api.api_request import ApiRequestor
from adapay.utils.param_handler import parse_to_adapay_object


class Refund(AdapayObject):
    OBJECT_NAME = 'refund'

    @classmethod
    def create(cls, **kwargs):
        """
        发起退款

         :param kwargs: 退款参数说明

        -------------必填-------------
        charge_id  原支付交易支付id
        order_no   退款订单号
        amount 退款金额，元

        -------------选填-------------
        description 退款描述
        extra 扩展域
        device_info 设备静态信息
        :return:
        """

        url = (adapay.base_url + '/v1/charges/{charge_id}/refunds').format(charge_id=kwargs.get('charge_id', ''))
        refund_dict = ApiRequestor.request(url, 'post', kwargs)
        return parse_to_adapay_object(refund_dict)

    @classmethod
    def query(cls, **kwargs):
        """
        退款查询
        两个单号填一个即可
        refund_id	退款返回订单号
        charge_id	原支付订单号
        """

        refund_dict = ApiRequestor.request(adapay.base_url + '/v1/charges/refunds', 'get', kwargs)
        return parse_to_adapay_object(refund_dict)

