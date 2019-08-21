"""
2019.8.1 create by yumin.chang
调用支付接口
"""

import adapay
from adapay.api.api_request import ApiRequestor


class Charge:
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
        return ApiRequestor.request(adapay.base_url + '/v1/charges', 'post', kwargs)

    @classmethod
    def query(cls, charge_id):
        """
        支付查询

        :param charge_id:
        :return:
        """
        url = (adapay.base_url + '/v1/charges/{charge_id}').format(charge_id=charge_id)
        return ApiRequestor.request(url, 'get', {'charge_id': charge_id})

    @classmethod
    def close(cls, **kwargs):
        """
        关单请求

        :param kwargs:
        :return:
        """
        url = (adapay.base_url + '/v1/charges/{}/close').format(kwargs['charge_id'])
        return ApiRequestor.request(url, 'post', kwargs)

# if __name__ == '__main__':
# import time
# import logging
#     # 全局变量
# adapay.private_key_path = 'D:\project\py_project\configuration_center_server\\application\\api\\rule\\release_private_key.pem'
# adapay.public_key_path = 'D:\project\py_project\configuration_center_server\\application\\api\\rule\\release_public_key.pem'
# adapay.api_key = 'api_live_3128984e-7c0f-4799-8c45-90e673870cb5'
#     adapay.log_level = logging.INFO
#     order_no = '2019010112000' + str(int(time.time()))
#
#     charge = adapay.Charge.create(order_no=order_no,
#                                   app_id='app_P000002052092068',
#                                   pay_channel='alipay_qr',
#                                   amount='0.01',
#                                   currency='cny',
#                                   subject='subject',
#                                   body='body',
#                                   # 以上为必填参数，以下为非必填参数
#                                   description='description',
#                                   time_expire='30000101000000',
#                                   device_info={'hahahaha': '4',
#                                                'device_ip': '127.0.0.1',
#                                                'device_mac': 'B0-83-FE-9B-F4-EE',
#                                                'device_imei': 'device_imei',
#                                                'device_imsi': 'device_imsi',
#                                                'device_iccId': 'device_iccId',
#                                                'device_wifi_mac': 'device_wifi_mac',
#                                                'device_gps': 'device_gps'},
#                                   extra={'promotion_detail': {'cost_price': '100.00',
#                                                               'receipt_id': '1',
#                                                               'goods_detail': {'goods_id': '123',
#                                                                                'goods_name': 'ipad',
#                                                                                'quantity': '1',
#                                                                                'price': '100.00',
#                                                                                'goods_category': 'goods_category',
#                                                                                'goods_body': 'goods_body',
#                                                                                'show_url': 'http://xxx.xxx.xxx'}
#                                                               }
#                                          }
#                                   )
#
#     print(charge['status'])

# query_result = adapay.Charge.query('002112019082110321810010076656381349888')
# print(query_result['status'])
# close_result= adapay.Charge.close(charge_id='002112019080920204500005876092564602880',
#                                       # 非必填
#                                       description='close_test',
#                                       extra={'test_key': 'test_value'})
