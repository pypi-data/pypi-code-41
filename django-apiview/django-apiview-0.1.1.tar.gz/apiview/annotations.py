import base64
import binascii
from fastutils import strutils

STRING_ENCODINGS = ["utf-8", "gb18030"]


def Boolean(obj):
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, str):
        if obj.lower() in ["true", "yes", "y", "1"]:
            return True
        else:
            return False
    if isinstance(obj, int):
        if obj != 0:
            return True
        else:
            return False
    if obj:
        return True
    else:
        return False


def Integer(obj):
    if isinstance(obj, int):
        return obj
    else:
        return int(obj)

def String(obj):
    if isinstance(obj, bytes):
        try:
            return obj.decode()
        except UnicodeDecodeError:
            for encoding in STRING_ENCODINGS:
                try:
                    return obj.decode(encoding)
                except UnicodeDecodeError:
                    pass
    return str(obj)


def Bytes(obj):
    if isinstance(obj, bytes):
        return obj
    if isinstance(obj, str):
        if strutils.is_unhexlifiable(obj):
            return binascii.unhexlify(obj)
        elif strutils.is_base64_decodable(obj):
            return base64.decodebytes(obj.encode())
        elif strutils.is_urlsafeb64_decodable(obj):
            return base64.urlsafe_b64decode(obj.encode())
        else:
            return obj.encode("utf-8")
    obj = str(obj)
    return obj.encode("utf-8")
