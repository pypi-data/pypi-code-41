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
        return ApiRequestor.request(url, 'post', kwargs)

    @classmethod
    def query(cls, **kwargs):
        """
        退款查询
        两个单号填一个即可
        refund_id	退款返回订单号
        charge_id	原支付订单号
        """

        return ApiRequestor.request(adapay.base_url + '/v1/charges/refunds', 'get', kwargs)

# if __name__ == '__main__':
#     adapay.private_key_path = 'D:\project\py_project\configuration_center_server\\application\\api\\rule\\release_private_key.pem'
#     adapay.api_key = 'api_live_44037605-a277-4f98-836b-10988130b186'
#
#     adapay.Refund.create(
#         # 必填
#         charge_id='002112019081517031900008000733122854912',
#         order_no='20190101120001565859799',
#         amount='0.01',
#         # 可选
#         description='测试退款',
#         extra={},
#         device_info={})
#
#     adapay.Refund.query(
#         refund_id='refund_id',
#         charge_id='002112019081517031900008000733122854912')
