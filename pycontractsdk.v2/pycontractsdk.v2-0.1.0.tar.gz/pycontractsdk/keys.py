#! /usr/bin/env python
# -*- coding: utf8 -*-
"""
# Author: yuyongpeng@hotmail.com
# Description: 用于签名和验证签名
#  

"""
from web3 import Web3
import eth_account
import eth_utils
import eth_keys
from eth_keys.backends import NativeECCBackend
import os
import re
from eth_keys import KeyAPI
from eth_keys.backends import NativeECCBackend


def get_key_and_address(length=32):
    """
    生成16进制的private_key
    :param length:
    :return:
    """
    iv = os.urandom(length)
    private_key = eth_utils.to_hex(iv)
    public_Key = privatekey_to_publickey(private_key)
    address = privatekey_to_address(private_key)
    return private_key, address, public_Key


def privatekey_to_publickey(private_key):
    """
    生成私钥对应的公钥address
    :param private_key: 私钥 (hex或bytes）
    :return:
    """
    if not eth_utils.is_bytes(private_key):
        private_key = eth_utils.decode_hex(eth_utils.add_0x_prefix(private_key))
    pk = eth_keys.keys.PrivateKey(private_key)
    return pk.public_key


def privatekey_to_address(private_key):
    """
    根据私钥获得对应的公钥
    :param private_key: 私钥 （hex或bytes）
    :return:
    """
    if not eth_utils.is_bytes(private_key):
        private_key = eth_utils.decode_hex(eth_utils.add_0x_prefix(private_key))
    pk = eth_keys.keys.PrivateKey(private_key)
    return pk.public_key.to_checksum_address()


def sig_message(message, private_key_hex):
    """
    对message数据进行签名
    :param message: 需要签名的数据，(bytes)
    :param private_key_hex: 签名用的私钥
    :return:
    """
    private_key_byte = eth_utils.decode_hex(eth_utils.add_0x_prefix(private_key_hex))
    pk = eth_keys.keys.PrivateKey(private_key_byte)
    print('public key: {}'.format(pk.public_key))
    print('public key to address:  {}'.format(pk.public_key.to_checksum_address()))
    signature = pk.sign_msg(message)
    return signature


def ecdsa_sign(message: str, private_key_hex) -> str:
    """
    对message数据进行签名 (sig_message方法返回的结果相同)
    :param message: 需要签名的数据，(bytes)如果输入的不是byte会自动转成bytes
    :param private_key_hex: 签名用的私钥  str
    :return: str类型的签名数据 hex
    """
    if isinstance(message, str):
        message = message.encode('utf8')
    message_hash = eth_utils.keccak(message)
    keys_api = eth_keys.KeyAPI(NativeECCBackend())
    private_key_byte = eth_utils.decode_hex(eth_utils.add_0x_prefix(private_key_hex))
    pk = eth_keys.keys.PrivateKey(private_key_byte)
    signature = keys_api.ecdsa_sign(message_hash, pk)
    return str(signature).lstrip('0x')


def ecdsa_verify(message: str, signature: str, public_key):
    """
    验证签名是否正确
    :param message: 需要验证的数据 string
    :param signature: 签名 hex
    :param public_key: 必须是长的字符串，里面可能有前缀，需要处理  string or bytes
    :return:
    """
    if not isinstance(message, str):
        raise ValueError('message = {}  must string'.format(message))
    if not isinstance(signature, str):
        raise ValueError('signature = {}  must string'.format(signature))

    pb = check_public_key(public_key)   # pb 必须是一个没有 0x 和 04 前缀的 bytes
    message_hash = eth_utils.keccak(message.encode('utf8'))
    keys_api = eth_keys.KeyAPI(NativeECCBackend())
    signature_bytes = eth_utils.decode_hex(eth_utils.add_0x_prefix(signature))
    signature_obj = keys_api.Signature(signature_bytes=bytes.fromhex(signature))
    PublicKey = keys_api.ecdsa_recover(message_hash, signature_obj)
    # address_public = PublicKey.to_checksum_address()
    if '0x{}'.format(pb.decode()) == str(PublicKey):
        return True
    else:
        return False


def get_vrs_signature(signature_hex):
    """
    获得签名数据的 R S V
    :param signature_hex: 签名的数据 hex
    :return: (R:bytes, S:bytes, V:int)
    """
    from eth_keys import validation
    from eth_keys.exceptions import ValidationError, BadSignature
    signature_bytes = eth_utils.decode_hex(signature_hex)
    validation.validate_signature_bytes(signature_bytes)
    try:
        r = signature_bytes[0:32]
        s = signature_bytes[32:64]
        v = ord(signature_bytes[64:65])
    except ValidationError as err:
        raise BadSignature(str(err))
    return r, s, v
    # keys_api = KeyAPI(NativeECCBackend())
    # signature_obj = keys_api.Signature(signature_bytes=signature_bytes)
    # return signature_obj.vrs


def value_to_hex(bts):
    """
    将二进制转换为hex（16进制）
    :param bts:
    :return:
    """
    return eth_utils.to_hex(bts)


def check_public_key(public_key):
    """
    监测public_key 返回正确的数据
    请注意，某些库在字节序列化公钥前面加上前导\x04字节，在使用PublicKey对象之前必须将其删除 。
    有一些public key 是带有前缀的，以太坊的public key 需要去掉前缀
    :param public_key: 公钥 (str 或者 bytes)
    :return:  返回bytes的字符串
    """
    if isinstance(public_key, bytes):
        public_key = public_key.decode()

    if isinstance(public_key, str):
        public_key_no0x = re.sub('^0x','',public_key)
        if len(public_key_no0x) == 128:
            public_key_str = public_key_no0x
        elif len(public_key_no0x) == 130:
            public_key_str = public_key_no0x[2:]
        else:
            raise ValueError('string public_key={} length not 128'.format(public_key))

    return public_key_str.encode()


def kaccke(value):
    """
    获得value对应的keccak的hash值
    :param value:
    :return: bytes数据
    """
    from eth_utils import keccak
    return keccak(value)


def is_privatekey(key):
    """
    监测private key长度是否正确
    必须是64位的长度
    """
    import re
    prog = re.compile('^[a-zA-Z0-9]{64}$')
    tf = prog.match(key)
    return tf


def to_check_sum_address(address):
    """
    将 address 进行checkSum
    :param address:
    :return:
    """
    normal_address = eth_utils.add_0x_prefix(address)
    return Web3.toChecksumAddress(normal_address)

# def private_key_to_address(private_key):
#     """
#     获得 private_key 对应的 address (这个地址是checkSum的)
#     :param private_key:
#     :return: address (这个地址是checkSum的)
#     """
#     acct = eth_account.Account.privateKeyToAccount(private_key)
#     return acct.address


# def private_key_to_public_key(private_key):
#     """
#     获得private_key对应的public_key
#     :param private_key:
#     :return: public_key
#     """
#     keys = KeyAPI(NativeECCBackend)
#     privateKey = keys.PrivateKey(bytes.fromhex(eth_utils.remove_0x_prefix(private_key)))
#     return privateKey.public_key
#
#
# def public_key_to_address(public_key):
#     """
#     获得 public_key 对应的 address (这个地址是checkSum的)
#     :param public_key:
#     :return: address (这个地址是checkSum的)
#     """
#     keys = KeyAPI(NativeECCBackend)
#     publicKey = keys.PublicKey(bytes.fromhex(eth_utils.remove_0x_prefix(public_key)))
#     return publicKey.to_checksum_address()


