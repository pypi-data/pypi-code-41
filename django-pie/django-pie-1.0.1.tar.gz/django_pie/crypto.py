# coding: utf-8
import base64
import hashlib


def _hashlib(name, s, upper=False) -> str:
    if isinstance(s, str):
        s = s.encode()
    ss = hashlib.new(name, s).hexdigest()
    return ss.upper() if upper else ss


def md5(s, upper=False) -> str:
    return _hashlib('md5', s, upper)


def sha1(s, upper=False) -> str:
    return _hashlib('sha1', s, upper)


def sha256(s, upper=False) -> str:
    return _hashlib('sha256', s, upper)


def b64encode(s) -> bytes:
    if isinstance(s, str):
        s = s.encode()
    return base64.b64encode(s)


def b64decode(s: bytes) -> bytes:
    return base64.b64decode(s)


# todo: ASE, DES, RSA
