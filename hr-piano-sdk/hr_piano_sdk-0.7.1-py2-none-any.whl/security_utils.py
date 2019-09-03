import base64
import hmac
import hashlib
import struct
from Crypto.Cipher import AES


class SecurityUtils(object):
    DELIM = '~~~'

    @staticmethod
    def encrypt(key, value):
        orig_key = key
        if len(key) > 32:
            key = key[:32]
        else:
            key = key + ("X" * (32 - len(key)))

        raw_key = str.encode(key)
        value_bytes = str.encode(value)

        crypt = AES.new(key=raw_key, mode=AES.MODE_ECB)

        out = b''

        for i in range(0, len(value_bytes), 16):
            if len(value_bytes) - i >= 16:
                encrypted = crypt.encrypt(value_bytes[i:i+16])
                out += encrypted
            else:
                padded_value_bytes = value_bytes[i:]
                pad_len = 16 - len(padded_value_bytes)
                padded_value_bytes = padded_value_bytes + (bytes([pad_len]) * pad_len)
                encrypted = crypt.encrypt(padded_value_bytes)
                out += encrypted

        safe = SecurityUtils.urlensafe(out)
        return safe + SecurityUtils.DELIM + SecurityUtils.urlensafe(
            hmac.new(str.encode(orig_key), str.encode(safe), digestmod=hashlib.sha256).digest())

    @staticmethod
    def decrypt(key, value):
        if SecurityUtils.DELIM in value:
            position = value.rindex(SecurityUtils.DELIM)
            cipher = value[:position]
            hmac_value = value[position + len(SecurityUtils.DELIM):]
            test_hmac = SecurityUtils.urlensafe(
                hmac.new(str.encode(key), str.encode(cipher), digestmod=hashlib.sha256).digest())
            if test_hmac != hmac_value:
                raise Exception("Could not parse message invalid hmac")
            value = cipher
        return SecurityUtils.decrypt_to_bytes(key, value)

    @staticmethod
    def decrypt_to_bytes(key_string, value):
        if len(key_string) > 32:
            key = key_string[:32]
        else:
            key = key_string + ("X" * (32 - len(key_string)))
        raw_key = str.encode(key)

        crypt = AES.new(key=raw_key, mode=AES.MODE_ECB)

        decrypted = SecurityUtils.urldesafe(value)

        out = b''
        for i in range(0, len(decrypted), 16):
            if i + 16 < len(decrypted):
                encrypted = crypt.decrypt(decrypted[i:i+16])
                out += encrypted
            else:
                encrypted = crypt.decrypt(decrypted[i:])
                out += SecurityUtils.unpad(encrypted)

        return out.decode()

    @staticmethod
    def unpad(out_buff):
        size = len(out_buff)
        pad_value = struct.unpack('B', out_buff[-1:])[0]

        if pad_value < 1 or pad_value > 16:
            return out_buff

        return out_buff[0:(size - pad_value)]

    @staticmethod
    def urlensafe(data):
        return base64.urlsafe_b64encode(data).decode().replace('=', '')

    @staticmethod
    def urldesafe(data):
        missing_padding = len(data) % 4
        if missing_padding != 0:
            data += '=' * (4 - missing_padding)
        return base64.urlsafe_b64decode(data)
