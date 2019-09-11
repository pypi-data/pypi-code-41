import hashlib
import json

from alipay.aop.api.util.EncryptUtils import aes_encrypt_content, aes_decrypt_content
from alipay.aop.api.util.SignatureUtils import get_sign_content, sign_with_rsa2, verify_with_rsa


def get_jsonstr_content(all_params, keep_raw_data=True, keep_space=True):
    """
    将键值对数据构造为待加密的字符串，该方法仅用于键值对类型（dict）的数据进行加密

    :param all_params: 键值对数据
    :param keep_raw_data: 对特殊字符，如汉字，是否保留原数据
    :param keep_space: 是否保留空格
    :return:
    """
    all_params = {value[0]: value[1] for value in sorted(all_params.items())}  # 按键进行字典排序
    return json.dumps(all_params, ensure_ascii=not keep_raw_data, separators=None if keep_space else (',', ':'))


def aes_encrypt(params, aes_key, keep_raw_data=True, keep_space=True, charset='utf-8'):
    """
    对键值对数据进行AES加密，采用的模式ECB模式

    :param params: 待加密数据
    :param aes_key: 加密的key，必须为32位
    :param keep_raw_data: 对特殊字符，如汉字，是否保留原数据
    :param keep_space: 是否保留空格
    :param charset: 编码，默认为utf-8
    :return: 加密后的字符串
    """
    if len(aes_key) != 32:
        raise Exception('aes_key 必须为32位，请检查')
    if isinstance(params, str):
        encrypt_str = params
    elif isinstance(params, dict):
        encrypt_str = get_jsonstr_content(params, keep_raw_data, keep_space)
    else:
        raise Exception('params的类型 必须是str或dict')
    encrypt_result = aes_encrypt_content(encrypt_str, aes_key, charset)
    return encrypt_result


def aes_decrypt(encrypt_result, aes_key, charset='utf-8'):
    """
    对加密数据进行解密，解密结果是一个字符串

    :param encrypt_result: 加密数据
    :param aes_key: 加密的key，必须为32位
    :param charset: 编码，默认为utf-8
    :return: 字符串
    """
    return aes_decrypt_content(encrypt_result, aes_key, charset)


def base_sha256(sign_content, charset='utf-8'):
    '''
    通用的SHA256哈希算法

    :param sign_content: 待签名数据
    :param charset: 编码格式
    :return:
    '''
    return hashlib.sha256(sign_content.encode(charset)).hexdigest()


def sha256_with_key(params, sha_name='sha_name', sha_key='sha_key', charset='utf-8'):
    """
    我方提供的SHA256加签名方法

    :param params: 待签名数据
    :param sha_name: 干扰码的名称
    :param sha_key: 干扰码
    :param charset: 编码格式
    :return:
    """
    if isinstance(params, str):
        sign_content = params
    elif isinstance(params, dict):
        sign_content = get_sign_content(params)
    else:
        raise Exception('params的类型 必须是str或dict')
    sign_content += '&{}={}'.format(sha_name, sha_key)
    sha_result = base_sha256(sign_content, charset)  # 获取基本哈希值
    return sha_result


def get_sign(params, pri_key, charset='utf-8'):
    '''
    使用RSA2WithSHA256，获取签名

    :param params: 待签名数据
    :param pri_key: 私钥
    :param charset: 编码格式
    :return:
    '''
    if isinstance(params, str):
        sign_content = params
    elif isinstance(params, dict):
        sign_content = get_sign_content(params)
    else:
        raise Exception('params的类型 必须是str或dict')
    return sign_with_rsa2(pri_key, sign_content, charset)


def check_sign(params, sign, public_key, charset='utf-8'):
    '''
    使用RSA2WithSHA256，校验签名

    :param params: 待验签数据
    :param public_key: 公钥
    :param charset: 编码格式
    :return:
    '''
    if isinstance(params, bytes):
        sign_content = params
    elif isinstance(params, str):
        sign_content = params.encode(charset)
    elif isinstance(params, dict):
        sign_content = get_sign_content(params).encode(charset)
    else:
        raise Exception('params的类型 必须是bytes、str或dict')
    return verify_with_rsa(public_key, sign_content, sign)
