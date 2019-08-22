import json
from typing import Dict, Mapping

import requests
from nezha.encryption.aes import AESCrypt
from nezha.hash import hash_md5


def generate_raw_biz_data(name: str, idcard: str, mobile: str) -> Dict:
    return locals()


def generate_param(raw_biz_data: Mapping, aes_key: str) -> str:
    return AESCrypt(aes_key).encrypt(json.dumps(raw_biz_data, sort_keys=True))


def generate_tokenKey(raw_biz_data: Mapping, param: str, url: str, token_id: str) -> str:
    data = {'param': param}
    data.update(raw_biz_data)
    param_string = ','.join(map(lambda x: '='.join(x), sorted(data.items(), key=lambda item: item[0])))
    return hash_md5(''.join((url, token_id, param_string)))


def generate_request_data(param: str, tokenKey: str, appId: str) -> Dict:
    return locals()


def _request(url, data):
    response = requests.post(url, data=data)
    if response.ok:
        return response.json()
    raise SystemError(f'response code {response.status_code} text {response.text}')


def request_assessment_radar(name: str, idcard: str, mobile: str,
                             app_id: str,
                             token_id: str,
                             aes_key: str,
                             url: str = 'http://api.tcredit.com/assessment/radar'):
    """
    free called
    :return:
    """
    raw_biz_data = generate_raw_biz_data(name, idcard, mobile)
    param = generate_param(raw_biz_data, aes_key)
    request_data = {
        'param': param,
        'tokenKey': generate_tokenKey(raw_biz_data, param, url, token_id),
        'appId': app_id
    }
    return _request(url, request_data)
