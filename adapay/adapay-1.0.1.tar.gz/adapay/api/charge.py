"""
2019.8.1 create by yumin.chang
调用支付接口
"""

import adapay
from adapay.adapay_obj import AdapayObject

from adapay.api.api_request import ApiRequestor
from adapay.utils.param_handler import parse_to_adapay_object


class Charge(AdapayObject):
    OBJECT_NAME = 'charge'

    """
    支付接口
    """

    @classmethod
    def create(cls, **kwargs):
        """
        创建 charge 对象

        -------------必传-------------
        order_no 订单号
        app_id 商户交易使用的应用对象 id
        pay_channel 支付渠道
        amount 订单总金额（必须大于0），人民币为元。
        currency 3位 ,ISO 货币代码，小写字母，人民币为 cny
        subject 商品标题
        body 商品描述信息

        -------------选填-------------
        description 订单附加说明
        time_expire 订单失效时间yyyyMMddHHmmSS，默认时间
        device_info 设备信息
        extra 额外优惠信息等

        :return
        """
        charge_dict = ApiRequestor.request(adapay.base_url + '/v1/charges', 'post', kwargs)
        return parse_to_adapay_object(charge_dict)

    @classmethod
    def query(cls, charge_id):
        """
        支付查询

        :param charge_id:
        :return:
        """
        url = (adapay.base_url + '/v1/charges/{charge_id}').format(charge_id=charge_id)
        charge_dict = ApiRequestor.request(url, 'get', {'charge_id': charge_id})
        return parse_to_adapay_object(charge_dict)

    @classmethod
    def close(cls, **kwargs):
        """
        关单请求

        :param kwargs:
        :return:
        """
        url = (adapay.base_url + '/v1/charges/{}/close').format(kwargs['charge_id'])
        charge_dict = ApiRequestor.request(url, 'post', kwargs)
        return parse_to_adapay_object(charge_dict)



