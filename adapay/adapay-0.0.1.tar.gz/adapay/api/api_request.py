"""
2019.8.1 create by jun.hu
默认请求对象
"""
import json

import requests

import adapay
from adapay.utils.log_util import log_error, log_info
from adapay.utils.param_handler import get_plain_text, read_pem
from adapay.utils.pycrypt_utils import rsa_sign, rsa_design


class ApiRequestor:

    @staticmethod
    def _build_request_info(url, method, params):
        """
        根据请求方式构造请求头和请求参数
        :return: header 请求头 params 请求参数
        """
        # 构造请求头
        header = {'Authorization': adapay.api_key,
                  'Content-type': 'application/json',
                  'Signature': ''}

        plain_text = url

        # 根据不通方法进行不同加签处理
        if method == 'post':
            params['sign_type'] = 'RSA2'
            plain_text = plain_text + json.dumps(params)
        elif method == 'get':

            plain_text = plain_text + get_plain_text(params)
            header.update({'Content-type': 'text/html'})

        # 获取商户密钥
        if adapay.private_key:
            private_key = adapay.private_key
        else:
            # 如果密钥为空则从外部传入地址读取
            private_key = read_pem(adapay.private_key_path)
            adapay.private_key = private_key

        # 对请求参数进行加签
        flag, cipher_text = rsa_sign(private_key, plain_text, 'utf-8')

        if not flag:
            log_error('request to {}, sign error {} '.format(url, cipher_text))

        # 将签名更新到请求头中
        header.update({'Signature': cipher_text})
        log_info('request to {}, param is {}, \nhead is {}'.format(url, params, header))

        return header, params

    @staticmethod
    def request(url, method, params):
        """
        执行请求
        :param url: 请求地址
        :param method: 请求方法类型
        :param params: 请求参数
        :return:
        """
        header, params = ApiRequestor._build_request_info(url, method, params)

        http_method = getattr(requests, method or 'post')

        if method == 'post':
            resp = http_method(url, json=params, timeout=adapay.connect_timeout, headers=header)

        else:
            resp = http_method(url, params, timeout=adapay.connect_timeout, headers=header)

        log_info('request to {}, resp is {}'.format(url, resp.text))

        resp_dict = ApiRequestor._build_return_data(resp)
        return resp_dict

    @staticmethod
    def _build_return_data(resp):

        resp_json = json.loads(resp.text)

        # 当业务请求成功时验证返回数据与签名
        if adapay.public_key:
            public_key = adapay.public_key
        else:
            public_key = read_pem(adapay.public_key_path)
            adapay.public_key = public_key

        data = resp_json.get('data', '')
        # 验证返回数据与返回加签结果是否一致
        flag, info = rsa_design(resp_json.get('signature', ''), data, public_key)

        if not flag:
            # 如果验签失败，抛出异常
            log_error('check signature error !'.format(info))
            raise RuntimeError(info)

        return json.loads(data)
