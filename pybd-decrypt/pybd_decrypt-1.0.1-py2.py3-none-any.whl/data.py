# -*- coding: utf-8 -*-

import base64
import json
import socket
import struct

from Crypto.Cipher import AES
from pywe_utils import to_binary


# Decrypt Algorithm
#   See: 用户数据的签名验证和加解密 - https://smartprogram.baidu.com/docs/develop/api/open_log/#%E7%94%A8%E6%88%B7%E6%95%B0%E6%8D%AE%E7%9A%84%E7%AD%BE%E5%90%8D%E9%AA%8C%E8%AF%81%E5%92%8C%E5%8A%A0%E8%A7%A3%E5%AF%86/


class WXBizDataCrypt:
    def __init__(self, sessionKey):
        self.sessionKey = sessionKey

    def decrypt(self, encryptedData, iv):
        # base64 decode
        sessionKey = base64.b64decode(to_binary(self.sessionKey + '='))
        encryptedData = base64.b64decode(encryptedData)
        iv = base64.b64decode(iv)

        cipher = AES.new(sessionKey, AES.MODE_CBC, iv[:16])

        decrypted = json.loads(self._unpad(cipher.decrypt(encryptedData)))

        return decrypted

    def _unpad(self, s):
        pad = ord(s[-1])
        # 去除 16 位随机字符串
        content = s[16:-pad]
        xml_len = socket.ntohl(struct.unpack('I', content[:4])[0])
        xml_content = content[4:xml_len + 4]
        return xml_content


def decrypt(sessionKey=None, encryptedData=None, iv=None):
    return WXBizDataCrypt(sessionKey).decrypt(encryptedData, iv)
