import os,sys
import hashlib
import base64
import pyDes


def md5(msg):
    """
        Args md5(str): is you want Encryption msg
    """
    m=hashlib.md5()
    m.update(str(msg).encode("utf8"))
    token=m.hexdigest()
    return token